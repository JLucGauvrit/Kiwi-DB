"""
LangGraph orchestrator for federated RAG query flow.

Ce module implémente l'orchestrateur RAG fédéré basé sur LangGraph.
Il gère le flux de traitement des requêtes utilisateur à travers
un pipeline d'agents spécialisés : intention, récupération de schéma,
génération SQL, validation, exécution et composition.

@author: PROCOM Team
@version: 1.0
@since: 2026-01-19
"""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.orchestrator.agent_registry import AgentRegistry


class QueryState(TypedDict):
    """
    État partagé pour le flux de traitement des requêtes.
    
    Cet état est passé entre tous les nœuds du graphe LangGraph
    et accumule les résultats intermédiaires du traitement.
    
    @var query: Requête utilisateur originale
    @type query: str
    @var intent: Résultats de la classification d'intention
    @type intent: dict
    @var schemas: Schémas de base de données récupérés
    @type schemas: list
    @var sql_queries: Requêtes SQL générées pour chaque base de données
    @type sql_queries: dict
    @var validation_results: Résultats de la validation des requêtes SQL
    @type validation_results: dict
    @var execution_results: Résultats de l'exécution des requêtes SQL
    @type execution_results: dict
    @var final_output: Réponse finale composée pour l'utilisateur
    @type final_output: str
    @var errors: Liste des erreurs rencontrées pendant le traitement
    @type errors: list
    """
    query: str
    intent: dict
    schemas: list
    sql_queries: dict
    validation_results: dict
    execution_results: dict
    final_output: str
    errors: list


class FederatedRAGOrchestrator:
    """
    Orchestrateur RAG fédéré basé sur LangGraph.
    
    Gère le flux complet de traitement des requêtes utilisateur
    à travers plusieurs agents spécialisés en utilisant LangGraph
    pour l'orchestration du pipeline.
    
    @param config: Configuration de l'orchestrateur
    @type config: dict
    
    @ivar config: Configuration contenant les URLs et paramètres
    @ivar registry: Registre des agents disponibles
    @ivar graph: Graphe LangGraph compilé du pipeline
    """
    
    def __init__(self, config: dict):
        """
        Initialiser l'orchestrateur RAG fédéré.
        
        @param config: Configuration contenant les URLs des services et paramètres du modèle
        @type config: dict
        """
        self.config = config
        self.registry = AgentRegistry(config)
        self.graph = self._build_graph()

    def _build_graph(self):
        """
        Construire le graphe LangGraph du pipeline de traitement.
        
        Crée un graphe avec les nœuds suivants :
        - intent : Classification de l'intention de la requête
        - retrieve : Récupération des schémas de bases de données
        - generate_sql : Génération des requêtes SQL
        - validate : Validation des requêtes SQL
        - execute : Exécution des requêtes SQL (conditionnel)
        - compose : Composition de la réponse finale
        
        @return: Graphe LangGraph compilé
        @rtype: CompiledStateGraph
        """
        workflow = StateGraph(QueryState)
        
        # Ajouter les nœuds du pipeline
        workflow.add_node("intent", self._intent_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate_sql", self._sql_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("compose", self._compose_node)
        
        # Définir les connexions entre les nœuds
        workflow.set_entry_point("intent")
        workflow.add_edge("intent", "retrieve")
        workflow.add_edge("retrieve", "generate_sql")
        workflow.add_edge("generate_sql", "validate")
        workflow.add_conditional_edges(
            "validate",
            self._should_execute,
            {"execute": "execute", "end": END}
        )
        workflow.add_edge("execute", "compose")
        workflow.add_edge("compose", END)
        
        return workflow.compile()

    def _intent_node(self, state: QueryState) -> QueryState:
        """
        Nœud d'intention : Classifier la requête utilisateur.
        
        Utilise l'agent d'intention pour déterminer si la requête
        nécessite un accès à la base de données ou si c'est une
        question de connaissances générales.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec l'intention classifiée
        @rtype: QueryState
        """
        agent = self.registry.get_agent("intent")
        state["intent"] = agent.run(state["query"])
        return state

    def _retrieve_node(self, state: QueryState) -> QueryState:
        """
        Nœud de récupération : Récupérer les schémas de base de données.
        
        Récupère les schémas des bases de données pertinentes
        basé sur l'intention détectée. Si l'accès à la base de données
        n'est pas nécessaire, définit un message d'erreur.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec les schémas récupérés
        @rtype: QueryState
        """
        # Ignorer la récupération si l'accès à la base de données n'est pas nécessaire
        if not state["intent"].get("requires_database", True):
            state["schemas"] = []
            state["final_output"] = "I can only answer questions about data in our databases (users, products, orders). Your question appears to be general knowledge that I cannot help with."
            return state
        
        agent = self.registry.get_agent("retriever")
        state["schemas"] = agent.run(state["intent"])
        return state

    def _sql_node(self, state: QueryState) -> QueryState:
        """
        Nœud de génération SQL : Générer les requêtes SQL.
        
        Utilise l'agent SQL pour générer les requêtes SQL
        basées sur l'intention et les schémas disponibles.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec les requêtes SQL générées
        @rtype: QueryState
        """
        agent = self.registry.get_agent("sql")
        state["sql_queries"] = agent.run(state["intent"], state["schemas"])
        return state

    def _validate_node(self, state: QueryState) -> QueryState:
        """
        Nœud de validation : Valider les requêtes SQL.
        
        Valide que les requêtes SQL générées sont correctes
        et conformes aux schémas disponibles.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec les résultats de validation
        @rtype: QueryState
        """
        agent = self.registry.get_agent("validator")
        state["validation_results"] = agent.run(state["sql_queries"], state["schemas"])
        return state

    def _execute_node(self, state: QueryState) -> QueryState:
        """
        Nœud d'exécution : Exécuter les requêtes SQL.
        
        Exécute les requêtes SQL validées sur les bases de données
        via la passerelle MCP.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec les résultats d'exécution
        @rtype: QueryState
        """
        from src.executor.query_runner import QueryRunner
        runner = QueryRunner(self.config)
        state["execution_results"] = runner.execute_federated(state["sql_queries"])
        return state

    def _compose_node(self, state: QueryState) -> QueryState:
        """
        Nœud de composition : Composer la réponse finale.
        
        Utilise l'agent de composition pour générer une réponse
        naturelle en langage humain basée sur les résultats
        de l'exécution des requêtes SQL.
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: État mis à jour avec la réponse finale composée
        @rtype: QueryState
        """
        agent = self.registry.get_agent("composer")
        state["final_output"] = agent.run(
            state["query"],
            state["execution_results"],
            state["sql_queries"]
        )
        return state

    def _should_execute(self, state: QueryState) -> str:
        """
        Fonction de décision conditionnelle : Déterminer s'il faut exécuter les requêtes.
        
        Vérifie plusieurs conditions :
        1. Si l'accès à la base de données est requis
        2. Si des requêtes SQL valides ont été générées
        3. Si les requêtes SQL sont validées
        
        @param state: État actuel du pipeline
        @type state: QueryState
        @return: "execute" pour exécuter les requêtes, "end" pour terminer sans exécuter
        @rtype: str
        """
        # Vérifier si l'accès à la base de données est requis
        if not state["intent"].get("requires_database", True):
            state["final_output"] = "This question doesn't require database access. I can only answer questions about data in our databases."
            state["errors"] = ["Query does not require database access"]
            return "end"
        
        # Vérifier si nous avons des requêtes SQL valides
        if not state["sql_queries"]:
            state["final_output"] = "I couldn't find relevant data in our databases to answer your question. Our databases contain information about: users, products, and orders."
            state["errors"] = ["No valid SQL queries generated"]
            return "end"
        
        # Vérifier les résultats de validation
        if state["validation_results"].get("valid", False):
            return "execute"
        
        state["errors"] = state["validation_results"].get("issues", [])
        return "end"

    def run(self, query: str) -> dict:
        """
        Exécuter le pipeline synchrone pour une requête donnée.
        
        @param query: Requête utilisateur
        @type query: str
        @return: État final contenant tous les résultats du traitement
        @rtype: dict
        """
        initial_state = {
            "query": query,
            "intent": {},
            "schemas": [],
            "sql_queries": {},
            "validation_results": {},
            "execution_results": {},
            "final_output": "",
            "errors": []
        }
        return self.graph.invoke(initial_state)
    
    async def run_async(self, query: str) -> dict:
        """
        Exécuter le pipeline asynchrone pour une requête donnée.
        
        @param query: Requête utilisateur
        @type query: str
        @return: État final contenant tous les résultats du traitement
        @rtype: dict
        """
        initial_state = {
            "query": query,
            "intent": {},
            "schemas": [],
            "sql_queries": {},
            "validation_results": {},
            "execution_results": {},
            "final_output": "",
            "errors": []
        }
        return await self.graph.ainvoke(initial_state)
