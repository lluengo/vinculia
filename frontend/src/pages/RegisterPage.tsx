import React, { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { UserPlus, AlertCircle, CheckCircle2, Circle, Loader2 } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validaciones en vivo
  const rules = useMemo(() => {
    return {
      minLength: password.length >= 8,
      hasUpper: /[A-Z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSpecial: /[!@#$%^&*(),.?":{}|<>]/.test(password),
      passwordsMatch: password.length > 0 && password === passwordConfirm,
    };
  }, [password, passwordConfirm]);

  const isFormValid =
    email.includes('@') &&
    rules.minLength &&
    rules.hasUpper &&
    rules.hasNumber &&
    rules.hasSpecial &&
    rules.passwordsMatch;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid) {
      setError('Por favor cumple con todos los requisitos de seguridad antes de continuar.');
      return;
    }

    setError(null);
    setIsSubmitting(true);

    try {
      await register(email, password, passwordConfirm);
      navigate('/dashboard');
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Error al registrar la cuenta. Verifica los datos ingresados.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center items-center gap-2">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-md">
            V
          </div>
          <span className="text-2xl font-bold text-slate-900 tracking-tight">Vinculia</span>
        </div>
        <h2 className="mt-4 text-center text-2xl font-extrabold text-slate-900">
          Crear Cuenta Profesional
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Únete a la plataforma para psicomotricistas y terapeutas
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <div className="bg-white py-8 px-6 shadow-sm border border-slate-200 rounded-2xl sm:px-10">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 rounded-r-lg flex items-center gap-3 text-red-700 text-sm">
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-slate-800">
                Correo Electrónico
              </label>
              <div className="mt-1">
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ejemplo@profesional.com"
                  className="appearance-none block w-full px-4 py-3 border border-slate-300 rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-base text-slate-900"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-slate-800">
                Contraseña
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Mínimo 8 caracteres"
                  className="appearance-none block w-full px-4 py-3 border border-slate-300 rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-base text-slate-900"
                />
              </div>
            </div>

            <div>
              <label htmlFor="passwordConfirm" className="block text-sm font-semibold text-slate-800">
                Confirmar Contraseña
              </label>
              <div className="mt-1">
                <input
                  id="passwordConfirm"
                  name="passwordConfirm"
                  type="password"
                  required
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  placeholder="Repite la contraseña"
                  className="appearance-none block w-full px-4 py-3 border border-slate-300 rounded-xl shadow-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent text-base text-slate-900"
                />
              </div>
            </div>

            {/* Panel de Validaciones en Vivo */}
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs space-y-2">
              <span className="font-bold text-slate-700 block mb-1">Requisitos de seguridad:</span>
              
              <div className="flex items-center gap-2">
                {rules.minLength ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-400" />
                )}
                <span className={rules.minLength ? 'text-emerald-700 font-medium' : 'text-slate-600'}>
                  Mínimo 8 caracteres
                </span>
              </div>

              <div className="flex items-center gap-2">
                {rules.hasUpper ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-400" />
                )}
                <span className={rules.hasUpper ? 'text-emerald-700 font-medium' : 'text-slate-600'}>
                  Al menos una letra mayúscula (A-Z)
                </span>
              </div>

              <div className="flex items-center gap-2">
                {rules.hasNumber ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-400" />
                )}
                <span className={rules.hasNumber ? 'text-emerald-700 font-medium' : 'text-slate-600'}>
                  Al menos un número (0-9)
                </span>
              </div>

              <div className="flex items-center gap-2">
                {rules.hasSpecial ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-400" />
                )}
                <span className={rules.hasSpecial ? 'text-emerald-700 font-medium' : 'text-slate-600'}>
                  Al menos un carácter especial (!@#$%^&*...)
                </span>
              </div>

              <div className="flex items-center gap-2 pt-1 border-t border-slate-200">
                {rules.passwordsMatch ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : (
                  <Circle className="w-4 h-4 text-slate-400" />
                )}
                <span className={rules.passwordsMatch ? 'text-emerald-700 font-medium' : 'text-slate-600'}>
                  Las contraseñas coinciden
                </span>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={!isFormValid || isSubmitting}
                className="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-md text-base font-semibold text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Creando cuenta...</span>
                  </>
                ) : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    <span>Registrarse</span>
                  </>
                )}
              </button>
            </div>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-600">
              ¿Ya tienes una cuenta registrada?{' '}
              <Link
                to="/login"
                className="font-semibold text-blue-600 hover:text-blue-700 underline decoration-2 underline-offset-4"
              >
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
