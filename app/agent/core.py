import os
from typing import Annotated, TypedDict
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from app.agent.tools import get_sentiment_analysis, get_summary_analysis, get_propagation_analysis

load_dotenv()

# Definición del estado del agente
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], lambda x, y: x + y]

class AtinnaAgent:
    def __init__(self):
        self.tools = [get_sentiment_analysis, get_summary_analysis, get_propagation_analysis]
        self.tool_node = ToolNode(self.tools)
        
        # El modelo real de OpenAI (ChatOpenAI) fue desactivado temporalmente debido a cuota insuficiente (Error 429).
        # Se utiliza directamente el agente de reglas (Mock LLM) para asegurar el funcionamiento de la demo.
            
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self):
        workflow = StateGraph(AgentState)

        # Definir nodos
        workflow.add_node("agent", self._call_model)
        workflow.add_node("action", self.tool_node)

        # Definir bordes
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        workflow.add_edge("action", "agent")

        return workflow

    def _should_continue(self, state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def _call_model(self, state: AgentState):
        messages = state["messages"]
        last_msg = messages[-1]
        
        # Si el último mensaje es de una HERRAMIENTA (ToolMessage), sintetizamos respuesta
        # En LangGraph, ToolNode devuelve una lista de ToolMessages
        if hasattr(last_msg, "tool_call_id") or "tool" in str(type(last_msg)).lower():
            tool_result = last_msg.content
            import json
            try:
                data = json.loads(tool_result) if isinstance(tool_result, str) else tool_result
            except:
                data = {"error": "No se pudo parsear el resultado"}

            # Sintetizar respuesta conversacional
            if "clima_general" in data:
                res = f"He analizado el clima de la conversación. El ambiente general es **{data['clima_general']}**. De una muestra de {data['total_analizado']} mensajes, encontré {data['conteo']['POSITIVE']} positivos y {data['conteo']['NEGATIVE']} negativos."
            elif "resumen_ejecutivo" in data:
                res = f"Aquí tienes el resumen ejecutivo: {data['resumen_ejecutivo']}\n\nTemas clave identificados: {', '.join(data['temas_clave'])}."
            elif "alcance" in data:
                res = f"El análisis de propagación para el mensaje {data.get('id_original')} indica un alcance de **{data['alcance']}** usuarios con una velocidad de respuesta de **{data['velocidad_media']}**."
                if "aviso" in data: res = f"*{data['aviso']}*\n\n" + res
            else:
                res = f"El análisis ha finalizado. Aquí están los datos técnicos: {str(data)}"
            
            return {"messages": [AIMessage(content=res)]}

        # Si es un mensaje del usuario, buscamos qué herramienta llamar
        last_query = last_msg.content.lower()
        
        tool_call = None
        if any(w in last_query for w in ["sentimiento", "clima", "polaridad", "ánimo", "ambiente"]):
            tool_call = {"name": "get_sentiment_analysis", "args": {}, "id": "call_sent"}
        elif any(w in last_query for w in ["resumen", "temática", "qué dicen", "principal", "tema"]):
            tool_call = {"name": "get_summary_analysis", "args": {}, "id": "call_sum"}
        elif any(w in last_query for w in ["propagación", "alcance", "viral", "difusión", "impacto", "mensaje"]):
            import re
            match = re.search(r"(\d+)", last_query)
            msg_id = match.group(1) if match else None
            tool_call = {"name": "get_propagation_analysis", "args": {"message_id": msg_id}, "id": "call_prop"}
        
        if tool_call:
            ai_msg = AIMessage(content="", tool_calls=[tool_call])
            return {"messages": [ai_msg]}
        else:
            if any(w in last_query for w in ["hola", "buenos", "tardes"]):
                res = "¡Hola! Soy Atinna AI. Puedo ayudarte con: \n1. **Análisis de sentimientos** (clima de la red)\n2. **Resumen ejecutivo** (temas clave)\n3. **Análisis de propagación** (impacto de un post)\n\n¿Qué te gustaría saber?"
            else:
                res = "Entiendo tu consulta, pero para ser más preciso, ¿te gustaría que realice un **resumen**, analice el **sentimiento** o vea la **propagación** de un mensaje?"
            return {"messages": [AIMessage(content=res)]}


    async def process_query(self, query: str):
        print(f"DEBUG: Procesando consulta con LangGraph: '{query}'")
        inputs = {"messages": [HumanMessage(content=query)]}
        
        # Ejecutar el grafo
        final_state = await self.app.ainvoke(inputs)
        
        # Retornar el contenido del último mensaje del agente
        last_msg = final_state["messages"][-1]
        
        # Si el último mensaje es del sistema (tool output), necesitamos que el agente lo interprete
        # Pero en este grafo, el agente siempre tiene la última palabra (después de 'action' vuelve a 'agent')
        return last_msg.content

