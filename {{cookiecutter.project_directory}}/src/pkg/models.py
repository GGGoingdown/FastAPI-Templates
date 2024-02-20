from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    password_hash = fields.CharField(max_length=255)

    class Meta:
        table = "users"
        table_description = "Users table"

    def __str__(self):
        return f"User(id={self.id}, email={self.email})"
