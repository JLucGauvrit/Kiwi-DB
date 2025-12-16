"""LangGraph orchestrator for federated RAG query flow."""
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from src.orchestrator.agent_registry import AgentRegistry


class QueryState(TypedDict):
    query: str
    intent: dict
    schemas: list
    sql_queries: dict
    validation_results: dict
    execution_results: dict
    final_output: str
    errors: list


class FederatedRAGOrchestrator:
    def __init__(self, config: dict):
        self.config = config
        self.registry = AgentRegistry(config)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(QueryState)
        
        # Add nodes
        workflow.add_node("intent", self._intent_node)
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("generate_sql", self._sql_node)
        workflow.add_node("validate", self._validate_node)
        workflow.add_node("execute", self._execute_node)
        workflow.add_node("compose", self._compose_node)
        
        # Define edges
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
        agent = self.registry.get_agent("intent")
        state["intent"] = agent.run(state["query"])
        return state

    def _retrieve_node(self, state: QueryState) -> QueryState:
        agent = self.registry.get_agent("retriever")
        state["schemas"] = agent.run(state["intent"])
        return state

    def _sql_node(self, state: QueryState) -> QueryState:
        agent = self.registry.get_agent("sql")
        state["sql_queries"] = agent.run(state["intent"], state["schemas"])
        return state

    def _validate_node(self, state: QueryState) -> QueryState:
        agent = self.registry.get_agent("validator")
        state["validation_results"] = agent.run(state["sql_queries"], state["schemas"])
        return state

    def _execute_node(self, state: QueryState) -> QueryState:
        from src.executor.query_runner import QueryRunner
        runner = QueryRunner(self.config)
        state["execution_results"] = runner.execute_federated(state["sql_queries"])
        return state

    def _compose_node(self, state: QueryState) -> QueryState:
        agent = self.registry.get_agent("composer")
        state["final_output"] = agent.run(
            state["query"],
            state["execution_results"],
            state["sql_queries"]
        )
        return state

    def _should_execute(self, state: QueryState) -> str:
        if state["validation_results"].get("valid", False):
            return "execute"
        state["errors"] = state["validation_results"].get("issues", [])
        return "end"

    def run(self, query: str) -> dict:
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
