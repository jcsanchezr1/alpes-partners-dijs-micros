import pytest
from datetime import datetime
from src.alpes_partners.modulos.contratos.dominio.entidades import Contrato
from src.alpes_partners.modulos.contratos.dominio.objetos_valor import (
    EstadoContrato, CategoriaContrato, TipoContrato, 
    InfluencerContrato, CampanaContrato, TerminosContrato,
    CompensacionContrato, PeriodoContrato
)
from src.alpes_partners.seedwork.dominio.objetos_valor import Dinero
from src.alpes_partners.seedwork.dominio.excepciones import ExcepcionReglaDeNegocio


class TestContrato:
    """Tests para la entidad Contrato."""
    
    def test_crear_contrato_exitoso(self):
        """Test crear contrato con datos válidos."""
        contrato = Contrato.crear(
            influencer_id="inf-123",
            influencer_nombre="Ana García",
            influencer_email="ana@example.com",
            campana_id="camp-456",
            campana_nombre="Campaña Verano 2024",
            categorias=["moda", "lifestyle"],
            descripcion="Contrato para promoción de productos de verano",
            monto_base=1500.0,
            moneda="USD",
            fecha_inicio=datetime(2024, 6, 1),
            fecha_fin=datetime(2024, 8, 31),
            tipo_contrato=TipoContrato.TEMPORAL
        )
        
        assert contrato.influencer.nombre == "Ana García"
        assert contrato.campana.nombre == "Campaña Verano 2024"
        assert contrato.estado == EstadoContrato.BORRADOR
        assert contrato.tipo_contrato == TipoContrato.TEMPORAL
        assert contrato.compensacion.monto_base.cantidad == 1500.0
        assert contrato.compensacion.monto_base.moneda == "USD"
    
    def test_contrato_sin_influencer_falla(self):
        """Test que falla al crear contrato sin influencer."""
        with pytest.raises(ExcepcionReglaDeNegocio):
            Contrato.crear(
                influencer_id="",
                influencer_nombre="",
                influencer_email="ana@example.com",
                campana_id="camp-456",
                campana_nombre="Campaña Verano 2024",
                categorias=["moda"],
                descripcion="Contrato de prueba",
                monto_base=1000.0,
                moneda="USD",
                fecha_inicio=datetime(2024, 6, 1)
            )
    
    def test_activar_contrato(self):
        """Test activar un contrato."""
        contrato = Contrato.crear(
            influencer_id="inf-123",
            influencer_nombre="Ana García",
            influencer_email="ana@example.com",
            campana_id="camp-456",
            campana_nombre="Campaña Verano 2024",
            categorias=["moda"],
            descripcion="Contrato de prueba",
            monto_base=1000.0,
            moneda="USD",
            fecha_inicio=datetime(2024, 6, 1)
        )
        
        # Cambiar a pendiente primero
        contrato.estado = EstadoContrato.PENDIENTE
        
        # Activar contrato
        contrato.activar_contrato()
        
        assert contrato.estado == EstadoContrato.ACTIVO
        assert contrato.fecha_firma is not None
    
    def test_finalizar_contrato(self):
        """Test finalizar un contrato activo."""
        contrato = Contrato.crear(
            influencer_id="inf-123",
            influencer_nombre="Ana García",
            influencer_email="ana@example.com",
            campana_id="camp-456",
            campana_nombre="Campaña Verano 2024",
            categorias=["moda"],
            descripcion="Contrato de prueba",
            monto_base=1000.0,
            moneda="USD",
            fecha_inicio=datetime(2024, 6, 1)
        )
        
        # Activar primero
        contrato.estado = EstadoContrato.PENDIENTE
        contrato.activar_contrato()
        
        # Finalizar
        contrato.finalizar_contrato()
        
        assert contrato.estado == EstadoContrato.COMPLETADO
        assert contrato.fecha_finalizacion is not None


class TestObjetosValorContrato:
    """Tests para los objetos de valor del dominio de contratos."""
    
    def test_categoria_contrato_valida(self):
        """Test crear categoría de contrato válida."""
        categoria = CategoriaContrato(["moda", "lifestyle", "belleza"])
        
        assert len(categoria.categorias) == 3
        assert "moda" in categoria.categorias
        assert "lifestyle" in categoria.categorias
        assert "belleza" in categoria.categorias
    
    def test_categoria_contrato_vacia_falla(self):
        """Test que falla al crear categoría vacía."""
        with pytest.raises(ValueError):
            CategoriaContrato([])
    
    def test_influencer_contrato_valido(self):
        """Test crear información de influencer válida."""
        influencer = InfluencerContrato(
            influencer_id="inf-123",
            nombre="Ana García",
            email="ana@example.com",
            plataformas_principales=["instagram", "tiktok"]
        )
        
        assert influencer.influencer_id == "inf-123"
        assert influencer.nombre == "Ana García"
        assert influencer.email == "ana@example.com"
        assert len(influencer.plataformas_principales) == 2
    
    def test_compensacion_contrato_valida(self):
        """Test crear compensación de contrato válida."""
        dinero = Dinero(2500.0, "EUR")
        compensacion = CompensacionContrato(
            monto_base=dinero,
            tipo_compensacion="por_entregable",
            bonificaciones={"bonus_engagement": 500.0}
        )
        
        assert compensacion.monto_base.cantidad == 2500.0
        assert compensacion.monto_base.moneda == "EUR"
        assert compensacion.tipo_compensacion == "por_entregable"
        assert compensacion.calcular_total_con_bonificaciones() == 3000.0
    
    def test_periodo_contrato_valido(self):
        """Test crear período de contrato válido."""
        inicio = datetime(2024, 6, 1)
        fin = datetime(2024, 8, 31)
        
        periodo = PeriodoContrato(
            fecha_inicio=inicio,
            fecha_fin=fin
        )
        
        assert periodo.fecha_inicio == inicio
        assert periodo.fecha_fin == fin
    
    def test_periodo_contrato_con_duracion(self):
        """Test crear período con duración en días."""
        inicio = datetime(2024, 6, 1)
        
        periodo = PeriodoContrato(
            fecha_inicio=inicio,
            duracion_dias=90
        )
        
        assert periodo.fecha_inicio == inicio
        assert periodo.fecha_fin is not None
        assert (periodo.fecha_fin - periodo.fecha_inicio).days == 90