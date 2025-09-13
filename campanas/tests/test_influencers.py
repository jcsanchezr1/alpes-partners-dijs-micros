import pytest
from datetime import datetime
from src.alpes_partners.modulos.influencers.dominio.entidades import Influencer
from src.alpes_partners.modulos.influencers.dominio.objetos_valor import EstadoInfluencer, CategoriaInfluencer
from src.alpes_partners.seedwork.dominio.objetos_valor import Email, Telefono
from src.alpes_partners.seedwork.dominio.excepciones import ExcepcionReglaDeNegocio


class TestInfluencer:
    """Tests para la entidad Influencer."""
    
    def test_crear_influencer_exitoso(self):
        """Test crear influencer con datos válidos."""
        influencer = Influencer.crear(
            nombre="Ana García",
            email="ana@example.com",
            categorias=["moda", "lifestyle"],
            descripcion="Influencer de moda y lifestyle con enfoque en sostenibilidad",
            biografia="Creadora de contenido apasionada por la moda sostenible",
            sitio_web="https://anagarcia.com",
            telefono="+34123456789"
        )
        
        assert influencer.nombre == "Ana García"
        assert influencer.email.valor == "ana@example.com"
        assert influencer.estado == EstadoInfluencer.PENDIENTE
        assert "moda" in influencer.perfil.categorias.categorias
        assert "lifestyle" in influencer.perfil.categorias.categorias
        assert len(influencer.eventos) == 1  # Evento InfluencerRegistrado
    
    def test_crear_influencer_sin_telefono(self):
        """Test crear influencer sin teléfono (campo opcional)."""
        influencer = Influencer.crear(
            nombre="Carlos López",
            email="carlos@example.com",
            categorias=["tecnologia", "gaming"],
            descripcion="Tech reviewer y gamer profesional"
        )
        
        assert influencer.nombre == "Carlos López"
        assert influencer.telefono is None
        assert influencer.estado == EstadoInfluencer.PENDIENTE
        assert len(influencer.eventos) == 1
    
    def test_crear_influencer_sin_nombre_falla(self):
        """Test que falla al crear influencer sin nombre."""
        with pytest.raises(ExcepcionReglaDeNegocio):
            Influencer.crear(
                nombre="",
                email="test@example.com",
                categorias=["tecnologia"],
                descripcion="Descripción"
            )
    
    def test_crear_influencer_email_invalido_falla(self):
        """Test que falla al crear influencer con email inválido."""
        with pytest.raises(ExcepcionReglaDeNegocio):
            Influencer.crear(
                nombre="Test User",
                email="email-invalido",
                categorias=["tecnologia"],
                descripcion="Descripción"
            )
    
    def test_crear_influencer_sin_categorias_falla(self):
        """Test que falla al crear influencer sin categorías."""
        with pytest.raises(ExcepcionReglaDeNegocio):
            Influencer.crear(
                nombre="Test User",
                email="test@example.com",
                categorias=[],
                descripcion="Descripción"
            )
    
    def test_es_compatible_con_categoria(self):
        """Test verificar compatibilidad con categorías."""
        influencer = Influencer.crear(
            nombre="María Rodríguez",
            email="maria@example.com",
            categorias=["moda", "belleza", "lifestyle"],
            descripcion="Beauty influencer"
        )
        
        assert influencer.es_compatible_con_categoria("moda")
        assert influencer.es_compatible_con_categoria("BELLEZA")  # Case insensitive
        assert influencer.es_compatible_con_categoria("lifestyle")
        assert not influencer.es_compatible_con_categoria("tecnologia")
    
    def test_puede_participar_en_campanas_sin_audiencia(self):
        """Test que influencer sin audiencia no puede participar en campañas."""
        influencer = Influencer.crear(
            nombre="Nuevo Influencer",
            email="nuevo@example.com",
            categorias=["moda"],
            descripcion="Nuevo en el mundo del marketing"
        )
        
        # Por defecto está en estado PENDIENTE y sin audiencia
        assert not influencer.puede_participar_en_campanas()
    
    def test_obtener_total_seguidores_sin_plataformas(self):
        """Test obtener total de seguidores cuando no hay plataformas."""
        influencer = Influencer.crear(
            nombre="Test Influencer",
            email="test@example.com",
            categorias=["tecnologia"],
            descripcion="Test description"
        )
        
        assert influencer.obtener_total_seguidores() == 0
    
    def test_obtener_engagement_promedio_sin_plataformas(self):
        """Test obtener engagement promedio cuando no hay plataformas."""
        influencer = Influencer.crear(
            nombre="Test Influencer",
            email="test@example.com",
            categorias=["tecnologia"],
            descripcion="Test description"
        )
        
        assert influencer.obtener_engagement_promedio() == 0.0
    
    def test_obtener_tipo_principal_sin_plataformas(self):
        """Test obtener tipo principal cuando no hay plataformas."""
        influencer = Influencer.crear(
            nombre="Test Influencer",
            email="test@example.com",
            categorias=["tecnologia"],
            descripcion="Test description"
        )
        
        assert influencer.obtener_tipo_principal() is None


if __name__ == "__main__":
    pytest.main([__file__])
