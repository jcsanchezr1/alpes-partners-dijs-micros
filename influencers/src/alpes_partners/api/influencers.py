import alpes_partners.seedwork.presentacion.api as api
import json
from typing import List, Optional
import logging

from flask import request, Response
from ..modulos.influencers.aplicacion.dto import InfluencerDTO
from ..modulos.influencers.aplicacion.servicios import ServicioInfluencer
from ..modulos.influencers.dominio.objetos_valor import TipoInfluencer, EstadoInfluencer, Plataforma
from ..modulos.influencers.dominio.excepciones import EmailYaRegistrado
from ..seedwork.aplicacion.comandos import ejecutar_commando
from ..seedwork.dominio.excepciones import ExcepcionDominio

# Importar el comando DIRECTAMENTE para registrarlo (como en el tutorial)
from ..modulos.influencers.aplicacion.comandos.registrar_influencer import RegistrarInfluencer

logger = logging.getLogger(__name__)

# Crear blueprint siguiendo el patrón del tutorial
bp = api.crear_blueprint('influencers', '/influencers')

# Importaciones para el servicio
from ..seedwork.infraestructura.uow import unidad_de_trabajo
from ..modulos.influencers.infraestructura.repositorio_sqlalchemy import RepositorioInfluencersSQLAlchemy


def obtener_servicio_influencer():
    """Función helper para obtener el servicio de influencers."""
    repositorio = RepositorioInfluencersSQLAlchemy()  # Sin parámetros, usa db.session
    uow = unidad_de_trabajo()  # Obtiene la UoW del contexto Flask
    return ServicioInfluencer(repositorio, uow)


@bp.route('/registrar-comando', methods=('POST',))
def registrar_influencer_asincrono():
    """Registra un nuevo influencer usando el patrón de comandos asíncrono."""
    try:
        datos_dict = request.json
        logger.info(f"API: Iniciando registro asíncrono de influencer - Email: {datos_dict.get('email')}")
        
        from datetime import datetime
        import uuid
        
        # Crear comando (siguiendo el patrón de CrearReserva)
        comando = RegistrarInfluencer(
            fecha_creacion=datetime.utcnow().isoformat(),
            fecha_actualizacion=datetime.utcnow().isoformat(),
            id=str(uuid.uuid4()),
            nombre=datos_dict.get('nombre'),
            email=datos_dict.get('email'),
            categorias=datos_dict.get('categorias', []),
            descripcion=datos_dict.get('descripcion', ''),
            biografia=datos_dict.get('biografia', ''),
            sitio_web=datos_dict.get('sitio_web', ''),
            telefono=datos_dict.get('telefono', '')
        )
        
        # TODO: Reemplazar este código síncrono y usar el broker de eventos para propagar este comando de forma asíncrona
        # Revisar la clase Despachador de la capa de infraestructura
        ejecutar_commando(comando)
        
        logger.info(f"API: Comando enviado exitosamente - Comando ID: {comando.id}")
        return Response(
            json.dumps({"mensaje": "Comando procesado", "comando_id": comando.id}),
            status=202,
            mimetype='application/json'
        )
        
    except EmailYaRegistrado as e:
        logger.warning(f"API: Email ya registrado en comando: {e}")
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
def listar_influencers():
    """Lista influencers con filtros opcionales."""
    try:
        logger.info("API: Iniciando consulta de influencers")
        
        # Obtener parámetros de query
        estado = request.args.get('estado')
        tipo = request.args.get('tipo')
        categoria = request.args.get('categoria')
        plataforma = request.args.get('plataforma')
        min_seguidores = request.args.get('min_seguidores', type=int)
        max_seguidores = request.args.get('max_seguidores', type=int)
        engagement_minimo = request.args.get('engagement_minimo', type=float)
        limite = request.args.get('limite', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Convertir strings a enums si es necesario
        if estado:
            estado = EstadoInfluencer(estado)
        if tipo:
            tipo = TipoInfluencer(tipo)
        if plataforma:
            plataforma = Plataforma(plataforma)
        
        servicio = obtener_servicio_influencer()
        resultado = servicio.listar_influencers(
            estado=estado,
            tipo=tipo,
            categoria=categoria,
            plataforma=plataforma,
            min_seguidores=min_seguidores,
            max_seguidores=max_seguidores,
            engagement_minimo=engagement_minimo,
            limite=limite,
            offset=offset
        )
        
        logger.info(f"API: Consulta exitosa - {len(resultado)} influencers encontrados")
        
        # Convertir DTOs a diccionarios para JSON
        resultado_dict = []
        for influencer_dto in resultado:
            # Manejar estado (puede ser enum o string)
            estado_valor = None
            if influencer_dto.estado:
                estado_valor = influencer_dto.estado.value if hasattr(influencer_dto.estado, 'value') else influencer_dto.estado
            
            # Manejar tipo_principal (puede ser enum o string)
            tipo_valor = None
            if hasattr(influencer_dto, 'tipo_principal') and influencer_dto.tipo_principal:
                tipo_valor = influencer_dto.tipo_principal.value if hasattr(influencer_dto.tipo_principal, 'value') else influencer_dto.tipo_principal
            
            resultado_dict.append({
                'id': influencer_dto.id,
                'nombre': influencer_dto.nombre,
                'email': influencer_dto.email,
                'categorias': influencer_dto.categorias,
                'descripcion': influencer_dto.descripcion,
                'biografia': influencer_dto.biografia,
                'sitio_web': influencer_dto.sitio_web,
                'telefono': influencer_dto.telefono,
                'estado': estado_valor,
                'tipo_principal': tipo_valor,
                'fecha_creacion': influencer_dto.fecha_creacion,
                'fecha_activacion': getattr(influencer_dto, 'fecha_activacion', None),
                'plataformas': getattr(influencer_dto, 'plataformas', []),
                'total_seguidores': getattr(influencer_dto, 'total_seguidores', 0),
                'engagement_promedio': getattr(influencer_dto, 'engagement_promedio', 0.0),
                'campanas_completadas': getattr(influencer_dto, 'campanas_completadas', 0),
                'cpm_promedio': getattr(influencer_dto, 'cpm_promedio', 0.0),
                'ingresos_generados': getattr(influencer_dto, 'ingresos_generados', 0.0)
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

