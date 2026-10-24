from app.models.entrevista import Entrevista

# Toda entrevista criada por aqui é "invisível" para o usuário: serve
# apenas para guardar as respostas dadas na tela de Perguntas (fora de uma
# simulação de entrevista completa), reaproveitando as tabelas já existentes
# de Entrevista/Resposta em vez de criar um novo modelo do zero.
TIPO_PRATICA = "pratica_perguntas"


class ObterEntrevistaPraticaService:
    """Busca a entrevista de prática do usuário autenticado, criando-a na
    primeira vez que ele responde alguma pergunta pelo banco de perguntas."""

    def __init__(self, usuario_id):
        self.usuario_id = usuario_id

    def execute(self):
        entrevista = (
            Entrevista.query
            .filter_by(usuario_id=self.usuario_id, tipo=TIPO_PRATICA)
            .order_by(Entrevista.id)
            .first()
        )
        if entrevista:
            return entrevista
        return Entrevista.criar(usuario_id=self.usuario_id, tipo=TIPO_PRATICA, status="em_andamento")
