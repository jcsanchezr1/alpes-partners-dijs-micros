import alpes_partners.seedwork.presentacion.api as api
import json
from typing import List, Optional
import logging

from flask import request, Response
from ..modulos.contratos.aplicacion.dto import ContratoDTO
from ..modulos.contratos.aplicacion.servicios import ServicioContrato
from ..modulos.contratos.dominio.objetos_valor import TipoContrato, EstadoContrato
from ..modulos.contratos.dominio.excepciones import ContratoYaExiste
from ..seedwork.aplicacion.comandos import ejecutar_commando
from ..seedwork.dominio.excepciones import ExcepcionDominio

# Importar el comando DIRECTAMENTE para registrarlo
from ..modulos.contratos.aplicacion.comandos.crear_contrato import CrearContrato

logger = logging.getLogger(__name__)

# Crear blueprint siguiendo el patrón del tutorial
bp = api.crear_blueprint('contratos', '/contratos')

# Importaciones para el servicio
from ..seedwork.infraestructura.uow import unidad_de_trabajo
from ..modulos.contratos.infraestructura.repositorio_sqlalchemy import RepositorioContratosSQLAlchemy


def obtener_servicio_contrato():
    """Función helper para obtener el servicio de contratos."""
    repositorio = RepositorioContratosSQLAlchemy()  # Sin parámetros, usa db.session
    uow = unidad_de_trabajo()  # Obtiene la UoW del contexto Flask
    return ServicioContrato(repositorio, uow)


@bp.route('/crear-comando', methods=('POST',))
def crear_contrato_asincrono():
    """Crea un nuevo contrato usando el patrón de comandos asíncrono."""
    try:
        datos_dict = request.json
        logger.info(f"API: Iniciando creación asíncrona de contrato")
        logger.info(f"API: Influencer: {datos_dict.get('influencer_nombre')}, Campaña: {datos_dict.get('campana_nombre')}")
        
        from datetime import datetime
        import uuid
        
        # Crear comando
        comando = CrearContrato(
            fecha_creacion=datetime.utcnow().isoformat(),
            fecha_actualizacion=datetime.utcnow().isoformat(),
            id=str(uuid.uuid4()),
            influencer_id=datos_dict.get('influencer_id'),
            influencer_nombre=datos_dict.get('influencer_nombre'),
            influencer_email=datos_dict.get('influencer_email'),
            campana_id=datos_dict.get('campana_id'),
            campana_nombre=datos_dict.get('campana_nombre'),
            categorias=datos_dict.get('categorias', []),
            descripcion=datos_dict.get('descripcion', ''),
            monto_base=datos_dict.get('monto_base', 0.0),
            moneda=datos_dict.get('moneda', 'USD'),
            fecha_inicio=datos_dict.get('fecha_inicio'),
            fecha_fin=datos_dict.get('fecha_fin'),
            entregables=datos_dict.get('entregables', ''),
            tipo_contrato=datos_dict.get('tipo_contrato', 'puntual')
        )
        
        # TODO: Reemplazar este código síncrono y usar el broker de eventos para propagar este comando de forma asíncrona
        ejecutar_commando(comando)
        
        logger.info(f"API: Comando enviado exitosamente - Comando ID: {comando.id}")
        return Response(
            json.dumps({"mensaje": "Comando procesado", "comando_id": comando.id}),
            status=202,
            mimetype='application/json'
        )
        
    except ContratoYaExiste as e:
        logger.warning(f"API: Contrato ya existe: {e}")
        return Response(
            json.dumps({"error": str(e)}),
            status=409,
            mimetype='application/json'
        )
    except ExcepcionDominio as e:
        logger.error(f"API: Error de dominio: {e}")
        return Response(
            json.dumps({"error": str(e)}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"API: Error interno: {e}", exc_info=True)
        return Response(
            json.dumps({"error": "Error interno del servidor"}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/', methods=('GET',))
def listar_contratos():
    """Lista contratos con filtros opcionales."""
    try:
        logger.info("API: Iniciando consulta de contratos")
        
        # Obtener parámetros de query
        estado = request.args.get('estado')
        tipo = request.args.get('tipo')
        categoria = request.args.get('categoria')
        influencer_id = request.args.get('influencer_id')
        campana_id = request.args.get('campana_id')
        monto_minimo = request.args.get('monto_minimo', type=float)
        monto_maximo = request.args.get('monto_maximo', type=float)
        limite = request.args.get('limite', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Convertir strings a enums si es necesario
        if estado:
            estado = EstadoContrato(estado)
        if tipo:
            tipo = TipoContrato(tipo)
        
        servicio = obtener_servicio_contrato()
        resultado = servicio.listar_contratos(
            estado=estado,
            tipo=tipo,
            categoria=categoria,
            influencer_id=influencer_id,
            campana_id=campana_id,
            monto_minimo=monto_minimo,
            monto_maximo=monto_maximo,
            limite=limite,
            offset=offset
        )
        
        logger.info(f"API: Consulta exitosa - {len(resultado)} contratos encontrados")
        
        # Convertir DTOs a diccionarios para JSON
        resultado_dict = []
        for contrato_dto in resultado:
            # Manejar estado (puede ser enum o string)
            estado_valor = None
            if contrato_dto.estado:
                estado_valor = contrato_dto.estado.value if hasattr(contrato_dto.estado, 'value') else contrato_dto.estado
            
            # Manejar tipo_contrato (puede ser enum o string)
            tipo_valor = None
            if contrato_dto.tipo_contrato:
                tipo_valor = contrato_dto.tipo_contrato.value if hasattr(contrato_dto.tipo_contrato, 'value') else contrato_dto.tipo_contrato
            
            resultado_dict.append({
                'id': contrato_dto.id,
                'influencer_id': contrato_dto.influencer_id,
                'influencer_nombre': contrato_dto.influencer_nombre,
                'influencer_email': contrato_dto.influencer_email,
                'campana_id': contrato_dto.campana_id,
                'campana_nombre': contrato_dto.campana_nombre,
                'estado': estado_valor,
                'tipo_contrato': tipo_valor,
                'categorias': contrato_dto.categorias,
                'descripcion': contrato_dto.descripcion,
                'entregables': contrato_dto.entregables,
                'monto_base': contrato_dto.monto_base,
                'moneda': contrato_dto.moneda,
                'fecha_inicio': contrato_dto.fecha_inicio,
                'fecha_fin': contrato_dto.fecha_fin,
                'fecha_creacion': contrato_dto.fecha_creacion,
                'fecha_firma': contrato_dto.fecha_firma,
                'fecha_finalizacion': contrato_dto.fecha_finalizacion,
                'entregables_completados': contrato_dto.entregables_completados,
                'engagement_alcanzado': contrato_dto.engagement_alcanzado,
                'costo_total': contrato_dto.costo_total,
                'roi_obtenido': contrato_dto.roi_obtenido
            })
        
        return Response(
            json.dumps(resultado_dict),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"API: Error en consulta: {e}", exc_info=True)
        return Response(
            json.dumps({"error": "Error interno del servidor"}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/vigentes', methods=('GET',))
def listar_contratos_vigentes():
    """Lista contratos vigentes."""
    try:
        logger.info("API: Consultando contratos vigentes")
        
        servicio = obtener_servicio_contrato()
        resultado = servicio.listar_contratos_vigentes()
        
        logger.info(f"API: {len(resultado)} contratos vigentes encontrados")
        
        # Convertir DTOs a diccionarios para JSON
        resultado_dict = []
        for contrato_dto in resultado:
            estado_valor = contrato_dto.estado.value if hasattr(contrato_dto.estado, 'value') else contrato_dto.estado
            tipo_valor = contrato_dto.tipo_contrato.value if hasattr(contrato_dto.tipo_contrato, 'value') else contrato_dto.tipo_contrato
            
            resultado_dict.append({
                'id': contrato_dto.id,
                'influencer_nombre': contrato_dto.influencer_nombre,
                'campana_nombre': contrato_dto.campana_nombre,
                'estado': estado_valor,
                'tipo_contrato': tipo_valor,
                'monto_base': contrato_dto.monto_base,
                'moneda': contrato_dto.moneda,
                'fecha_inicio': contrato_dto.fecha_inicio,
                'fecha_fin': contrato_dto.fecha_fin
            })
        
        return Response(
            json.dumps(resultado_dict),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"API: Error en consulta de vigentes: {e}", exc_info=True)
        return Response(
            json.dumps({"error": "Error interno del servidor"}),
            status=500,
            mimetype='application/json'
        )
