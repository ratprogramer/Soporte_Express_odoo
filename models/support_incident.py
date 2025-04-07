from odoo import fields, models  # type:ignore


class SupportIncident(models.fields):
    _name = "support.incident"
    _description = "Soporte de incidentes "

    name = fields.Char(required=True)
    description = fields.Text()
    category = fields.Selection([
        ("servicio_cliente", "Servicio Cliente"),
        ("soporte", "Soporte"),
        ("recursos_humanos", "Recursos Humanos")
    ], required=True, string="Categoria")

    priority = fields.Selection([
        ("baja", "Baja"),
        ("media", "Media"),
        ("alta", "Alta")], required=True, string="Prioridad"
    )

    state = fields.Selection([
        ("ingresado", "Ingresado"),
        ("proceso", "Proceso"),
        ("resuelto", "Resuelto")], default="Ingresado", required=True, string="Estado"
    )

    user_id = fields.Many2one(related="res.parner")
    deadline = fields.Date(required=True, string="Fecha limite")

    def send_notification(self):

        return self.env.ref('Soporte_Expr-s_odoo.cambio_estado').send_mail(self.id, force_send=True)

    def write(self, vals):
        # Guardamos los estados actuales de cada registro antes de la actualización
        old_states = {record.id: record.state for record in self}
        # Super realiza cambios en la base de datos
        result = super(SupportIncident, self).write(vals)
        # Recorremos los registros y verificamos si el estado cambió
        for record in self:
            if 'state' in vals and old_states.get(record.id) != record.state:
                record._send_notification()
        return result

    def cambiar_estado(self):
        for record in self:
            if record.state == "ingresado":
                record.state = "proceso"
            elif record.state == "proceso":
                record.state = "resuelto"
            elif record.state == "resuelto":
                record.state = "cerrado"
        # Puedes agregar más pasos si necesitas
