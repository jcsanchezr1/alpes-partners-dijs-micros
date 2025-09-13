from pulsar.schema import *
from alpes_partners.seedwork.infraestructura.schema.v1.comandos import ComandoIntegracion


class RegistrarInfluencerPayload(Record):
    id_usuario = String()
    nombre = String()
    email = String()
    categorias = Array(String())
    descripcion = String()
    biografia = String()
    sitio_web = String()
    telefono = String()


class ComandoRegistrarInfluencer(ComandoIntegracion):
    data = RegistrarInfluencerPayload()
