class DomainException(Exception):
    """Excepción base del dominio."""
    pass


class ProfesionalAlreadyExistsException(DomainException):
    """Lanzada cuando un profesional con el mismo email ya existe."""
    def __init__(self, email: str):
        super().__init__(f"El profesional con email '{email}' ya se encuentra registrado.")
        self.email = email


class InvalidCredentialsException(DomainException):
    """Lanzada cuando las credenciales proporcionadas no son válidas."""
    def __init__(self, message: str = "Credenciales inválidas."):
        super().__init__(message)


class ProfesionalNotFoundException(DomainException):
    """Lanzada cuando no se encuentra un profesional."""
    def __init__(self, identifier: str):
        super().__init__(f"Profesional no encontrado: {identifier}")
        self.identifier = identifier


class InvalidTokenException(DomainException):
    """Lanzada cuando un token JWT o de autenticación es inválido o ha expirado."""
    def __init__(self, message: str = "Token inválido o expirado."):
        super().__init__(message)


class GoogleAuthException(DomainException):
    """Lanzada cuando falla la validación con Google OAuth."""
    def __init__(self, message: str = "Error en la autenticación con Google."):
        super().__init__(message)


class PacienteNotFoundException(DomainException):
    """Lanzada cuando no se encuentra un paciente."""
    def __init__(self, identifier: str = ""):
        super().__init__(f"Paciente no encontrado: {identifier}")
        self.identifier = identifier


class ActividadNotFoundException(DomainException):
    """Lanzada cuando no se encuentra una actividad."""
    def __init__(self, identifier: str = ""):
        super().__init__(f"Actividad no encontrada: {identifier}")
        self.identifier = identifier


class TokenInvalidoException(DomainException):
    """Lanzada cuando un token de actividad es inexistente, inválido o ha expirado."""
    def __init__(self, message: str = "Enlace no válido o expirado."):
        super().__init__(message)


class ActividadInvalidaException(DomainException):
    """Lanzada cuando los datos de configuración o pares de una actividad son inválidos."""
    def __init__(self, message: str = "Datos de actividad inválidos."):
        super().__init__(message)

