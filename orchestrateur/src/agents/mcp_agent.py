"""Agent qui utilise OpenRouter avec tool calling MCP."""
import json
import logging
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from src.mcp_client import MCPGatewayClient

logger = logging.getLogger(__name__)


class MCPAgent:
    """Agent qui utilise le LLM OpenRouter avec les outils MCP via function calling."""

    def __init__(self, config: dict):
        self.config = config
        api_key = config.get("openrouter_api_key", "")
        model = config.get("openrouter_model", "nvidia/nemotron-3-nano-30b-a3b:free")

        self.llm = ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            model=model,
            temperature=0.1
        )

        gateway_url = config.get("mcp_gateway_url", "ws://mcp-gateway:9000")
        self.mcp_client = MCPGatewayClient(gateway_url)
        self.mcp_tools = []

    async def initialize(self):
        """Initialise l'agent en récupérant les outils MCP disponibles de tous les serveurs."""
        try:
            # Liste des serveurs MCP disponibles
            mcp_servers = ["postgres", "mongo", "mysql"]

            self.mcp_tools = []

            # Récupérer les outils de chaque serveur MCP (avec retry)
            for server_name in mcp_servers:
                loaded = False
                for attempt in range(3):
                    try:
                        logger.info(f"Loading tools from {server_name} (attempt {attempt + 1})...")
                        response = await self.mcp_client.list_tools(server=server_name)

                        if response.get("success"):
                            tools_data = response.get("tools", [])

                            for tool_info in tools_data:
                                if isinstance(tool_info, dict) and "name" in tool_info:
                                    tool_info_with_server = tool_info.copy()
                                    original_name = tool_info["name"]
                                    tool_info_with_server["name"] = f"{server_name}_{original_name}"
                                    tool_info_with_server["description"] = f"[{server_name.upper()}] {tool_info.get('description', '')}"
                                    tool_info_with_server["_server"] = server_name
                                    tool_info_with_server["_original_name"] = original_name

                                    tool_def = self._convert_mcp_tool_to_langchain(tool_info_with_server)
                                    self.mcp_tools.append(tool_def)

                            logger.info(f"Loaded {len(tools_data)} tools from {server_name}")
                            loaded = True
                            break
                        else:
                            logger.warning(f"Failed to load tools from {server_name} (attempt {attempt + 1}): {response}")

                    except Exception as e:
                        logger.error(f"Error loading tools from {server_name} (attempt {attempt + 1}): {e}")

                if not loaded:
                    logger.error(f"Could not load tools from {server_name} after 3 attempts")

            logger.info(f"Total tools loaded: {len(self.mcp_tools)}")

            # Bind tools to LLM
            if self.mcp_tools:
                self.llm = self.llm.bind_tools(self.mcp_tools)

        except Exception as e:
            logger.error(f"Error initializing MCP agent: {e}", exc_info=True)

    def _convert_mcp_tool_to_langchain(self, mcp_tool: Dict) -> Dict:
        """Convertit un outil MCP au format LangChain/OpenAI function calling."""
        tool_name = mcp_tool.get("name", "unknown")
        tool_description = mcp_tool.get("description", "")
        input_schema = mcp_tool.get("inputSchema", {})

        return {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_description,
                "parameters": input_schema
            }
        }

    async def process_query(self, user_query: str, max_iterations: int = 10, target_databases: list = None) -> Dict[str, Any]:
        """
        Traite une requête utilisateur en utilisant le LLM avec tool calling.

        Args:
            user_query: La requête de l'utilisateur
            max_iterations: Nombre maximum d'itérations pour éviter les boucles infinies

        Returns:
            Dictionnaire contenant les résultats et la réponse finale
        """
        try:
            # S'assurer que les outils sont chargés
            if not self.mcp_tools:
                await self.initialize()

            # Filtrer les outils selon les databases cibles
            if target_databases:
                active_tools = [
                    t for t in self.mcp_tools
                    if any(t['function']['name'].startswith(db + "_") for db in target_databases)
                ]
                # Si 0 outils trouvés, forcer un rechargement (cas où l'init a échoué)
                if not active_tools:
                    logger.warning(f"No tools found for {target_databases}, forcing reload...")
                    self.mcp_tools = []
                    await self.initialize()
                    active_tools = [
                        t for t in self.mcp_tools
                        if any(t['function']['name'].startswith(db + "_") for db in target_databases)
                    ]
                logger.info(f"Filtering tools for databases {target_databases}: {len(active_tools)} tools selected")
            else:
                active_tools = self.mcp_tools

            logger.info(f"Processing query: {user_query}")
            logger.info(f"Available tools: {[t['function']['name'] for t in active_tools]}")

            # Bind les outils filtrés au LLM
            llm_with_tools = self.llm if not active_tools else ChatOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.config.get("openrouter_api_key", ""),
                model=self.config.get("openrouter_model", ""),
                temperature=0.1
            ).bind_tools(active_tools)

            # Générer la liste des outils disponibles pour l'utilisateur
            tools_description = "\n".join([
                f"- {tool['function']['name']}: {tool['function']['description']}"
                for tool in active_tools
            ])

            messages = [
                HumanMessage(content=f"""Tu es un assistant expert en bases de données. Tu DOIS utiliser les outils ci-dessous pour accéder aux données. Tu n'as PAS besoin de chaîne de connexion ni de credentials — les outils gèrent la connexion à ta place.

OUTILS DISPONIBLES (utilise-les directement):
{tools_description}

RÈGLES STRICTES:
- Utilise UNIQUEMENT les outils listés ci-dessus pour interroger les données. Ne demande JAMAIS de chaîne de connexion à l'utilisateur.
- Appelle UN outil à la fois. Dès que tu as les données suffisantes, réponds en français sans appeler d'autres outils.
- Pour MySQL: utilise l'outil mysql_* avec une requête SQL directe (ex: SELECT * FROM livres).
- Pour MongoDB: utilise d'abord `mongo_list-databases`, puis `mongo_list-collections`, puis **`mongo_aggregate`** (avec `$limit`) pour récupérer les documents. Évite `mongo_find` qui est instable.
- Pour PostgreSQL: utilise l'outil postgres_* avec une requête SQL.
- Maximum 3 appels d'outils au total.

QUESTION: {user_query}""")
            ]

            tool_calls_made = []
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Iteration {iteration}/{max_iterations}")

                # Appeler le LLM
                response = await llm_with_tools.ainvoke(messages)
                messages.append(response)

                # Vérifier si le LLM veut appeler des outils
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    logger.info(f"LLM wants to call {len(response.tool_calls)} tools")

                    # Exécuter chaque outil demandé
                    for tool_call in response.tool_calls:
                        tool_name = tool_call.get("name")
                        tool_args = tool_call.get("args", {})
                        tool_id = tool_call.get("id", f"call_{iteration}")

                        logger.info(f"Calling tool: {tool_name} with args: {tool_args}")

                        # Exécuter l'outil via MCP Gateway
                        tool_result = await self._execute_mcp_tool(tool_name, tool_args)

                        tool_calls_made.append({
                            "tool": tool_name,
                            "arguments": tool_args,
                            "result": tool_result
                        })

                        # Ajouter le résultat à la conversation
                        messages.append(
                            ToolMessage(
                                content=json.dumps(tool_result, ensure_ascii=False),
                                tool_call_id=tool_id
                            )
                        )

                    # Continuer la boucle pour laisser le LLM traiter les résultats
                    continue

                else:
                    # Le LLM a fini - il a donné une réponse finale
                    logger.info("LLM provided final answer")
                    final_answer = response.content

                    # Vérifier si le LLM a utilisé des outils
                    if not tool_calls_made:
                        logger.warning("LLM answered without using any tools - possible hallucination")
                        final_answer = (
                            "⚠️ ATTENTION: Cette réponse n'est pas basée sur les données réelles de la base. "
                            "Le modèle LLM n'a pas pu accéder aux outils nécessaires.\n\n"
                            f"Réponse du modèle: {final_answer}\n\n"
                            "Veuillez reformuler votre question de manière plus précise."
                        )

                    return {
                        "success": True,
                        "query": user_query,
                        "tool_calls": tool_calls_made,
                        "answer": final_answer,
                        "iterations": iteration,
                        "warning": "no_tools_used" if not tool_calls_made else None
                    }

            # Si on atteint le maximum d'itérations
            logger.warning(f"Reached max iterations ({max_iterations})")
            return {
                "success": False,
                "query": user_query,
                "error": "Maximum iterations reached",
                "tool_calls": tool_calls_made,
                "iterations": iteration
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "success": False,
                "query": user_query,
                "error": str(e)
            }
        finally:
            await self.mcp_client.disconnect()

    async def _execute_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Exécute un outil MCP via la gateway."""
        try:
            # Extraire le nom du serveur et le nom original de l'outil
            # Format: "server_toolname" -> server="server", tool="toolname"
            if "_" in tool_name:
                parts = tool_name.split("_", 1)
                server_name = parts[0]
                original_tool_name = parts[1]
            else:
                # Fallback si pas de préfixe (ne devrait pas arriver)
                server_name = "postgres"
                original_tool_name = tool_name

            logger.info(f"Executing {original_tool_name} on {server_name} server")

            response = await self.mcp_client.call_tool(
                tool=original_tool_name,
                arguments=arguments,
                server=server_name
            )

            if response.get("success"):
                result = response.get("result", {})

                # Extraire le contenu si c'est une structure MCP
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].get("content", [])
                    if content and len(content) > 0:
                        text_content = content[0].get("text", "")
                        # Essayer de parser le JSON si possible
                        try:
                            return json.loads(text_content)
                        except:
                            return text_content

                return result
            else:
                error_msg = response.get("error", "Unknown error")
                logger.error(f"MCP tool execution failed: {error_msg}")
                return {"error": error_msg}

        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name}: {e}")
            return {"error": str(e)}
