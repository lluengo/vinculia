import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getActividadPublica, crearSesionPublica } from '../services/api';
import { ActividadPublica } from '../types';
import { Trophy, Clock, CheckCircle2, RotateCcw, AlertTriangle } from 'lucide-react';
import { MediaViewer, isAudioUrl } from '../components/MediaViewer';
import { resolveMediaUrl } from '../services/api';


export const PlayPage: React.FC = () => {
  const { token } = useParams<{ token: string }>();
  const [actividad, setActividad] = useState<ActividadPublica | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Gameplay state
  const [selectedOrigen, setSelectedOrigen] = useState<string | null>(null);
  const [asociaciones, setAsociaciones] = useState<Record<string, string>>({});
  const [completed, setCompleted] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState<number>(300);
  const [aciertos, setAciertos] = useState(0);
  const [errores, setErrores] = useState(0);

  useEffect(() => {
    if (!token) {
      setError('Token no proporcionado');
      setLoading(false);
      return;
    }

    getActividadPublica(token)
      .then((data) => {
        setActividad(data);
        const time = data.configuracion?.limite_tiempo_seg || 300;
        setSecondsLeft(time);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'Actividad no encontrada o enlace expirado');
      })
      .finally(() => setLoading(false));
  }, [token]);

  // Timer countdown
  useEffect(() => {
    if (completed || secondsLeft <= 0 || !actividad) return;
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          handleFinish();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [completed, secondsLeft, actividad]);

  const playSound = (url: string) => {
    try {
      const audio = new Audio(resolveMediaUrl(url));
      audio.play().catch(() => {});
    } catch {}
  };

  const handleSelectOrigen = (origen: string) => {
    if (completed) return;
    setSelectedOrigen(origen);
    if (isAudioUrl(origen)) {
      playSound(origen);
    }
  };

  const handleSelectDestino = (destino: string) => {
    if (isAudioUrl(destino) || actividad?.modo === 'imagen-sonido') {
      playSound(destino);
    }

    if (!selectedOrigen || completed) return;

    // Verificar si es par correcto
    const parCorrespondiente = actividad?.pares.find(
      (p) => p.origen_url === selectedOrigen && p.destino_url === destino
    );

    if (parCorrespondiente && parCorrespondiente.es_correcto) {
      setAsociaciones((prev) => ({ ...prev, [selectedOrigen]: destino }));
      setAciertos((a) => a + 1);
      setSelectedOrigen(null);

      // Comprobar si completó todos
      const totalPares = actividad?.pares.length || 0;
      if (Object.keys(asociaciones).length + 1 >= totalPares) {
        handleFinish();
      }
    } else {
      setErrores((e) => e + 1);
      setSelectedOrigen(null);
    }
  };

  const handleFinish = async () => {
    setCompleted(true);
    const tiempoUsado = (actividad?.configuracion?.limite_tiempo_seg || 300) - secondsLeft;
    try {
      await crearSesionPublica({
        token,
        tiempo_segundos: Math.max(1, tiempoUsado),
        aciertos: aciertos + 1,
        errores: errores,
      });
    } catch (e) {
      console.error('Error al registrar sesión pública', e);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-600 font-semibold">Cargando tu juego...</p>
        </div>
      </div>
    );
  }

  if (error || !actividad) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl p-8 max-w-md w-full text-center shadow-xl border border-slate-200 space-y-4">
          <div className="w-16 h-16 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center mx-auto">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-slate-800">Enlace no disponible</h2>
          <p className="text-slate-500 text-sm">
            {error || 'El enlace que buscas no existe o ha caducado. Consulta con tu profesional a cargo.'}
          </p>
        </div>
      </div>
    );
  }

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60);
    const remainder = secs % 60;
    return `${mins}:${remainder < 10 ? '0' : ''}${remainder}`;
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-between p-6 md:p-10 font-sans">
      {/* Play Header */}
      <header className="max-w-4xl mx-auto w-full flex items-center justify-between bg-white px-6 py-4 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <h1 className="text-xl md:text-2xl font-extrabold text-blue-600 tracking-tight">
            {actividad.titulo}
          </h1>
          {actividad.apodo_paciente ? (
            <p className="text-xs text-slate-500">
              ¡Hola <span className="font-bold text-slate-700">{actividad.apodo_paciente}</span>, a jugar!
            </p>
          ) : (
            <p className="text-xs text-slate-400">{actividad.descripcion || 'Empareja los elementos'}</p>
          )}
        </div>

        <div className="flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-xl font-bold text-sm">
          <Clock className="w-4 h-4" />
          <span>{formatTime(secondsLeft)}</span>
        </div>
      </header>

      {/* Main Game Area */}
      <main className="max-w-4xl mx-auto w-full my-8">
        {completed ? (
          <div className="bg-white rounded-3xl p-10 text-center shadow-xl border border-slate-100 space-y-6 max-w-lg mx-auto animate-in fade-in">
            <div className="w-20 h-20 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto shadow-inner">
              <Trophy className="w-10 h-10 animate-bounce" />
            </div>
            <div>
              <h2 className="text-3xl font-black text-slate-800">¡Excelente Trabajo! 🎉</h2>
              <p className="text-slate-500 mt-2">Has completado todos los ejercicios con éxito.</p>
            </div>

            <div className="grid grid-cols-2 gap-4 bg-slate-50 p-4 rounded-2xl text-center">
              <div>
                <p className="text-xs text-slate-400 font-bold uppercase">Aciertos</p>
                <p className="text-2xl font-black text-emerald-600">{aciertos}</p>
              </div>
              <div>
                <p className="text-xs text-slate-400 font-bold uppercase">Intentos</p>
                <p className="text-2xl font-black text-blue-600">{aciertos + errores}</p>
              </div>
            </div>

            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-2xl shadow-lg shadow-blue-600/30 transition"
            >
              <RotateCcw className="w-5 h-5" />
              <span>Jugar de Nuevo</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Columna Origen */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 text-center">
                Paso 1: Elige un elemento
              </h3>
              <div className="space-y-3">
                {actividad.pares.map((par, i) => {
                  const isMatched = Boolean(asociaciones[par.origen_url]);
                  const isSelected = selectedOrigen === par.origen_url;

                  return (
                    <button
                      key={i}
                      disabled={isMatched}
                      onClick={() => handleSelectOrigen(par.origen_url)}
                      className={`w-full p-4 rounded-2xl font-bold text-base transition-all duration-200 text-left flex items-center justify-between border-2 ${
                        isMatched
                          ? 'bg-emerald-50 border-emerald-300 text-emerald-800 opacity-60 cursor-default'
                          : isSelected
                          ? 'bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-600/30 scale-102'
                          : 'bg-white border-slate-200 text-slate-700 hover:border-blue-400 shadow-sm'
                      }`}
                    >
                      <div className="flex items-center gap-3 truncate">
                        <MediaViewer
                          content={par.origen_url}
                          className={isSelected ? 'text-white' : ''}
                        />
                      </div>
                      {isMatched && <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Columna Destino */}
            <div className="space-y-4">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 text-center">
                Paso 2: Asócialo con su pareja
              </h3>
              <div className="space-y-3">
                {actividad.pares.map((par, i) => {
                  const isMatched = Object.values(asociaciones).includes(par.destino_url);

                  return (
                    <div
                      key={i}
                      className={`w-full p-4 rounded-2xl font-bold text-base transition-all duration-200 flex items-center justify-between border-2 ${
                        isMatched
                          ? 'bg-emerald-50 border-emerald-300 text-emerald-800 opacity-60 cursor-default'
                          : selectedOrigen
                          ? 'bg-white border-dashed border-blue-300 text-slate-700 hover:bg-blue-50 hover:border-blue-500 cursor-pointer'
                          : 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed'
                      }`}
                      onClick={() => handleSelectDestino(par.destino_url)}
                    >
                      <div className="flex items-center gap-2">
                        {isMatched ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                        ) : (
                          <span className="text-xs font-normal text-slate-400">Unir aquí</span>
                        )}
                      </div>

                      <div className="flex items-center gap-3">
                        <MediaViewer
                          content={par.destino_url}
                          isAudioDestino={actividad.modo === 'imagen-sonido'}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-slate-400">
        Plataforma de Estimulación Cognitiva Vinculia • Diseñado para niños y profesionales
      </footer>
    </div>
  );
};
