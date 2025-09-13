from datetime import datetime
from typing import Optional, Dict, List
from ....seedwork.dominio.entidades import AgregacionRaiz
from ....seedwork.dominio.objetos_valor import Email, Telefono
from ....seedwork.dominio.excepciones import ExcepcionReglaDeNegocio, ExcepcionEstadoInvalido
from .objetos_valor import (
    TipoInfluencer, EstadoInfluencer, PerfilInfluencer, 
    MetricasInfluencer, CategoriaInfluencer, DatosAudiencia,
    Demografia, Plataforma
)
from .eventos import InfluencerRegistrado
from .excepciones import PlataformaNoSoportada, DatosAudienciaInvalidos


class Influencer(AgregacionRaiz):
    """Agregado raíz para Influencer."""
    
    def __init__(self, 
                 nombre: str,
                 email: Email,
                 perfil: PerfilInfluencer,
                 telefono: Optional[Telefono] = None,
                 id: Optional[str] = None):
        super().__init__(id)
        self.nombre = nombre.strip()
        self.email = email
        self.telefono = telefono
        self.perfil = perfil
        self.estado = EstadoInfluencer.PENDIENTE
        self.metricas = MetricasInfluencer()
        self.audiencia_por_plataforma: Dict[Plataforma, DatosAudiencia] = {}
        self.demografia: Optional[Demografia] = None
        self.fecha_activacion: Optional[datetime] = None
        self.fecha_desactivacion: Optional[datetime] = None
        
        # Validaciones
        if not self.nombre:
            raise ExcepcionReglaDeNegocio("El nombre del influencer es requerido")
    
    @classmethod
    def crear(cls, 
              nombre: str,
              email: str,
              categorias: list,
              descripcion: str,
              biografia: str = "",
              sitio_web: str = "",
              telefono: str = "") -> 'Influencer':
        """Factory method para crear un influencer."""
        
        email_obj = Email(email)
        telefono_obj = Telefono(telefono) if telefono else None
        categoria_obj = CategoriaInfluencer(categorias)
        
        perfil = PerfilInfluencer(
            categorias=categoria_obj,
            descripcion=descripcion,
            biografia=biografia,
            sitio_web=sitio_web
        )
        
        return cls(
            nombre=nombre,
            email=email_obj,
            perfil=perfil,
            telefono=telefono_obj
        )
    
    def crear_influencer(self, influencer: 'Influencer') -> None:
        """Método para procesar la creación del influencer (similar a crear_reserva)."""
        # Este método puede contener lógica adicional de validación o procesamiento
        # Por ahora, simplemente valida que el influencer esté en estado correcto
        if self.estado != EstadoInfluencer.PENDIENTE:
            raise ExcepcionEstadoInvalido("El influencer debe estar en estado PENDIENTE para ser procesado")
        
        # Emitir evento de registro
        self.agregar_evento(InfluencerRegistrado(
            influencer_id=self.id,
            nombre=self.nombre,
            email=self.email.valor,
            categorias=self.perfil.categorias.categorias,
            plataformas=[],  # Se actualizará cuando se agreguen plataformas
            fecha_registro=self.fecha_creacion
        ))
    
    def obtener_tipo_principal(self) -> Optional[TipoInfluencer]:
        """Obtiene el tipo de influencer basado en la plataforma con más seguidores."""
        if not self.audiencia_por_plataforma:
            return None
        
        plataforma_principal = max(
            self.audiencia_por_plataforma.values(),
            key=lambda x: x.seguidores
        )
        
        return plataforma_principal.calcular_tipo_influencer()
    
    def obtener_engagement_promedio(self) -> float:
        """Calcula el engagement promedio across todas las plataformas."""
        if not self.audiencia_por_plataforma:
            return 0.0
        
        total_engagement = sum(datos.engagement_rate for datos in self.audiencia_por_plataforma.values())
        return total_engagement / len(self.audiencia_por_plataforma)
    
    def obtener_total_seguidores(self) -> int:
        """Obtiene el total de seguidores across todas las plataformas."""
        return sum(datos.seguidores for datos in self.audiencia_por_plataforma.values())
