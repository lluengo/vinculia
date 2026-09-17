import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import {
  getActividad,
  createActividad,
  updateActividad,
  getPacientes,
  generarEnlace,
} from '../services/api';
import { Par, Paciente } from '../types';
import {
  ArrowLeft,
  Plus,
  Trash2,
  Save,
  Link as LinkIcon,
  Sparkles,
  AlertCircle,
  Eye,
  Settings2,

  Clock,
  Check,
  Copy,
  X,
  Upload,
} from 'lucide-react';
import { MediaViewer } from '../components/MediaViewer';
import { subirAssets } from '../services/api';

export const ConfiguradorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  // Form states
  const [titulo, setTitulo] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [modo, setModo] = useState('imagen-imagen');
  const [pacienteId, setPacienteId] = useState<string>('');
  const [limiteTiempoMin, setLimiteTiempoMin] = useState(5);
  const [nivelDificultad, setNivelDificultad] = useState(1);
  const [tamanoElementos, setTamanoElementos] = useState('mediano');
  const [toleranciaErrores, setToleranciaErrores] = useState(3);
  const [pares, setPares] = useState<Par[]>([
    { origen_url: '🐶 Perro', destino_url: '🦴 Hueso', es_correcto: true },
    { origen_url: '🐱 Gato', destino_url: '🐟 Pescado', es_correcto: true },
  ]);

  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedId, setSavedId] = useState<string | null>(id || null);
  const [errorMsg, setErrorMsg] = useState('');

  // Enlace modal
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [generatedLink, setGeneratedLink] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    // Cargar lista de pacientes para el selector
    getPacientes(1, 100).then((res) => {
      setPacientes(res.items);
    }).catch(console.error);

    // Si es edición, cargar la actividad existente
    if (id) {
      setLoading(true);
      getActividad(id)
        .then((act) => {
          setTitulo(act.titulo);
          setDescripcion(act.descripcion || '');
          setModo(act.modo);
          setPacienteId(act.paciente_id || '');
          if (act.configuracion) {
            setLimiteTiempoMin(Math.round((act.configuracion.limite_tiempo_seg || 300) / 60));
            setNivelDificultad(act.configuracion.nivel_dificultad || 1);
            setTamanoElementos(act.configuracion.tamano_elementos || 'mediano');
            setToleranciaErrores(act.configuracion.tolerancia_errores || 3);
          }
          if (act.pares && act.pares.length > 0) {
            setPares(act.pares);
          }
        })
        .catch((_err) => {
          setErrorMsg('No se pudo cargar la actividad');
        })

        .finally(() => setLoading(false));
    }
  }, [id]);

  const handleAddPar = () => {
    setPares([...pares, { origen_url: '', destino_url: '', es_correcto: true }]);
  };

  const handleRemovePar = (index: number) => {
    setPares(pares.filter((_, i) => i !== index));
  };

  const handleParChange = (index: number, field: keyof Par, value: any) => {
    const newPares = [...pares];
    newPares[index] = { ...newPares[index], [field]: value };
    setPares(newPares);
  };

  const handleUploadFile = async (index: number, field: 'origen_url' | 'destino_url', file: File) => {
    if (!savedId) {
      alert('Guarda la actividad primero para poder subir y almacenar archivos de audio o imagen en el servidor.');
      return;
    }
    const formData = new FormData();
    formData.append('files', file);

    try {
      const res = await subirAssets(savedId, formData);
      if (res.uploaded_files && res.uploaded_files.length > 0) {
        handleParChange(index, field, res.uploaded_files[0]);
      }
    } catch (err: any) {
      alert('Error al subir el archivo: ' + (err.response?.data?.detail || 'Error en el servidor'));
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!titulo.trim()) {
      setErrorMsg('El título del ejercicio es obligatorio');
      return;
    }
    if (pares.length === 0) {
      setErrorMsg('Debes agregar al menos un par de asociación');
      return;
    }

    setSaving(true);
    setErrorMsg('');

    const payload = {
      titulo: titulo.trim(),
      descripcion: descripcion.trim() || null,
      modo,
      paciente_id: pacienteId || null,
      tipo_plantilla: 'asociacion',
      pares,
      configuracion: {
        limite_tiempo_seg: limiteTiempoMin * 60,
        nivel_dificultad: nivelDificultad,
        tamano_elementos: tamanoElementos,
        tolerancia_errores: toleranciaErrores,
      },
    };

    try {
      if (savedId) {
        await updateActividad(savedId, payload);
      } else {
        const created = await createActividad(payload);
        setSavedId(created.id);
      }
      navigate('/actividades');
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Error al guardar la actividad');
    } finally {
      setSaving(false);
    }
  };

  const handleGenerateLink = async () => {
    const actId = savedId || id;
    if (!actId) return;
    try {
      const data = await generarEnlace(actId);
      const origin = window.location.origin;
      setGeneratedLink(`${origin}${data.url_completa}`);
      setCopied(false);
      setLinkModalOpen(true);
    } catch (err: any) {
      alert('Error al generar enlace: ' + (err.response?.data?.detail || 'Error'));
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="p-12 text-center text-slate-500">Cargando datos del ejercicio...</div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Navigation */}
        <div className="flex items-center justify-between bg-white p-4 px-6 rounded-2xl border border-slate-200/80 shadow-sm">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/actividades')}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-xl font-bold text-slate-800">
                {isEditing ? 'Editar Ejercicio de Asociación' : 'Configurador de Plantilla 1: Asociación'}
              </h2>
              <p className="text-xs text-slate-400">Estimulación cognitiva y psicomotora</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {savedId && (
              <button
                type="button"
                onClick={handleGenerateLink}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-sm rounded-xl shadow-sm transition"
              >
                <LinkIcon className="w-4 h-4" />
                <span>Generar Enlace</span>
              </button>
            )}
            <button
              onClick={handleSave}
              disabled={saving}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-blue-600/20 transition disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Guardando...' : 'Guardar Plantilla'}</span>
            </button>
          </div>
        </div>

        {errorMsg && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Two Panels Layout: Preview (Left) & Form (Right) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* PANEL IZQUIERDO: Preview en Vivo (5 columnas) */}
          <div className="lg:col-span-5 space-y-4">
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm sticky top-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
                <div className="flex items-center gap-2">
                  <Eye className="w-5 h-5 text-blue-600" />
                  <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">
                    Vista Previa en Vivo
                  </h3>
                </div>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  Modo Infantil Activo
                </span>
              </div>

              {/* Mockup Canvas */}
              <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-5 min-h-[380px] flex flex-col justify-between">
                <div>
                  <div className="text-center mb-4">
                    <span className="text-xs font-bold text-blue-600 uppercase tracking-widest bg-blue-50 px-2.5 py-0.5 rounded-full">
                      Plantilla Asociación • {modo}
                    </span>
                    <h4 className="text-lg font-bold text-slate-800 mt-2">
                      {titulo || 'Título del Ejercicio'}
                    </h4>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {descripcion || 'Empareja los elementos correspondientes'}
                    </p>
                  </div>

                  {/* Pares Preview Cards */}
                  <div className="space-y-2.5 my-4">
                    {pares.length === 0 ? (
                      <div className="text-center py-8 text-slate-400 text-xs">
                        Agrega pares en el configurador para visualizarlos aquí.
                      </div>
                    ) : (
                      pares.map((par, i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between p-3 bg-white rounded-xl border border-slate-200 shadow-sm text-xs font-semibold text-slate-700"
                        >
                          <div className="flex items-center gap-2 flex-1 truncate">
                            <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                              {i + 1}
                            </span>
                            <div className="truncate">
                              {par.origen_url ? (
                                <MediaViewer content={par.origen_url} />
                              ) : (
                                <span className="text-slate-400 italic">Elemento Origen</span>
                              )}
                            </div>
                          </div>
                          <span className="text-slate-300 font-bold px-2 flex-shrink-0">➔</span>
                          <div className="flex-1 truncate text-right text-blue-600 flex justify-end">
                            {par.destino_url ? (
                              <MediaViewer
                                content={par.destino_url}
                                isAudioDestino={modo === 'imagen-sonido'}
                              />
                            ) : (
                              <span className="text-slate-400 italic">Elemento Destino</span>
                            )}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Footer preview stats */}
                <div className="pt-3 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> {limiteTiempoMin} min
                  </span>
                  <span>Dificultad: Nivel {nivelDificultad}</span>
                  <span>Errores max: {toleranciaErrores}</span>
                </div>
              </div>
            </div>
          </div>

          {/* PANEL DERECHO: Formulario (7 columnas) */}
          <div className="lg:col-span-7 space-y-6">
            {/* General Info Card */}
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider flex items-center gap-2">
                <Settings2 className="w-4 h-4 text-blue-600" />
                Información Principal
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Título de la Actividad *
                  </label>
                  <input
                    type="text"
                    required
                    value={titulo}
                    onChange={(e) => setTitulo(e.target.value)}
                    placeholder="Ej: Reconocimiento de Frutas y Colores"
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Descripción / Consigna para el Niño
                  </label>
                  <textarea
                    rows={2}
                    value={descripcion}
                    onChange={(e) => setDescripcion(e.target.value)}
                    placeholder="Ej: Une con una línea cada fruta con el color que le corresponde."
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                      Modo Sensorial
                    </label>
                    <select
                      value={modo}
                      onChange={(e) => setModo(e.target.value)}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                    >
                      <option value="imagen-imagen">Imagen ➔ Imagen</option>
                      <option value="imagen-sonido">Imagen ➔ Sonido</option>
                      <option value="texto-imagen">Texto ➔ Imagen</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                      Paciente Asignado (Opcional)
                    </label>
                    <select
                      value={pacienteId}
                      onChange={(e) => setPacienteId(e.target.value)}
                      className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                    >
                      <option value="">Plantilla General (Sin paciente)</option>
                      {pacientes.map((p) => (
                        <option key={p.id} value={p.id}>
                          {p.apodo} {p.edad ? `(${p.edad} años)` : ''}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Parámetros Psicomotores & Dificultad */}
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
              <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-600" />
                Configuración y Accesibilidad
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between items-center mb-1.5">
                    <label className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                      Límite de Tiempo: {limiteTiempoMin} min
                    </label>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="10"
                    step="1"
                    value={limiteTiempoMin}
                    onChange={(e) => setLimiteTiempoMin(parseInt(e.target.value, 10))}
                    className="w-full accent-blue-600 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                    <span>1 min</span>
                    <span>5 min</span>
                    <span>10 min</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Nivel de Dificultad
                  </label>
                  <select
                    value={nivelDificultad}
                    onChange={(e) => setNivelDificultad(parseInt(e.target.value, 10))}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  >
                    <option value={1}>Nivel 1 - Muy Fácil (Iniciación)</option>
                    <option value={2}>Nivel 2 - Fácil</option>
                    <option value={3}>Nivel 3 - Moderado</option>
                    <option value={4}>Nivel 4 - Desafiante</option>
                    <option value={5}>Nivel 5 - Experto</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Tamaño de Elementos (Táctil)
                  </label>
                  <select
                    value={tamanoElementos}
                    onChange={(e) => setTamanoElementos(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  >
                    <option value="pequeno">Pequeño</option>
                    <option value="mediano">Mediano (Recomendado Tablet)</option>
                    <option value="grande">Grande (Motricidad reducida)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Tolerancia de Errores
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="10"
                    value={toleranciaErrores}
                    onChange={(e) => setToleranciaErrores(parseInt(e.target.value, 10))}
                    className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  />
                  <p className="text-[11px] text-slate-400 mt-1">Intentos antes de mostrar pista.</p>
                </div>
              </div>
            </div>

            {/* Editor de Pares */}
            <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wider">
                  Pares de Asociación ({pares.length})
                </h3>
                <button
                  type="button"
                  onClick={handleAddPar}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-600 font-semibold text-xs rounded-xl hover:bg-blue-100 transition"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>+ Agregar Par</span>
                </button>
              </div>

              <div className="space-y-4">
                {pares.map((par, index) => (
                  <div
                    key={index}
                    className="p-4 bg-slate-50 border border-slate-200 rounded-2xl space-y-3"
                  >
                    <div className="flex items-center justify-between text-xs font-bold text-slate-500">
                      <span>Par #{index + 1}</span>
                      <button
                        type="button"
                        onClick={() => handleRemovePar(index)}
                        className="p-1.5 text-slate-400 hover:text-red-500 rounded-lg hover:bg-red-50 transition"
                        title="Eliminar este par"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 items-start">
                      {/* Origen */}
                      <div className="space-y-1.5">
                        <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                          Origen (Texto, Emoji o Imagen)
                        </label>
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            placeholder="Ej: 🐶 o https://.../perro.png"
                            value={par.origen_url}
                            onChange={(e) => handleParChange(index, 'origen_url', e.target.value)}
                            className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <label
                            className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 cursor-pointer text-slate-500 hover:text-blue-600 transition"
                            title="Subir imagen/archivo desde tu PC"
                          >
                            <Upload className="w-4 h-4" />
                            <input
                              type="file"
                              accept="image/*,audio/*"
                              className="hidden"
                              onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                  handleUploadFile(index, 'origen_url', e.target.files[0]);
                                }
                              }}
                            />
                          </label>
                        </div>
                      </div>

                      {/* Destino */}
                      <div className="space-y-1.5">
                        <label className="block text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                          {modo === 'imagen-sonido'
                            ? 'Destino (URL Audio o archivo .mp3/.wav)'
                            : 'Destino (Texto o Imagen)'}
                        </label>
                        <div className="flex items-center gap-2">
                          <input
                            type="text"
                            placeholder={
                              modo === 'imagen-sonido'
                                ? 'https://.../sonido.mp3'
                                : 'Ej: 🦴 o https://.../hueso.png'
                            }
                            value={par.destino_url}
                            onChange={(e) => handleParChange(index, 'destino_url', e.target.value)}
                            className="flex-1 px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                          <label
                            className="p-2 bg-white border border-slate-200 rounded-xl hover:bg-slate-100 cursor-pointer text-slate-500 hover:text-blue-600 transition"
                            title="Subir audio o archivo desde tu PC"
                          >
                            <Upload className="w-4 h-4" />
                            <input
                              type="file"
                              accept="audio/*,image/*"
                              className="hidden"
                              onChange={(e) => {
                                if (e.target.files && e.target.files[0]) {
                                  handleUploadFile(index, 'destino_url', e.target.files[0]);
                                }
                              }}
                            />
                          </label>
                        </div>
                      </div>
                    </div>

                    {/* Preescucha / Vista Rápida del Par */}
                    {(par.origen_url || par.destino_url) && (
                      <div className="pt-2 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-500">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] uppercase font-bold text-slate-400">Preescucha:</span>
                          <MediaViewer content={par.origen_url} />
                        </div>
                        <span className="text-slate-300 font-bold">➔</span>
                        <div className="flex items-center gap-2">
                          <MediaViewer
                            content={par.destino_url}
                            isAudioDestino={modo === 'imagen-sonido'}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Modal Enlace */}
        {linkModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-base font-bold text-slate-800">Enlace Generado Exitosamente</h3>
                <button
                  onClick={() => setLinkModalOpen(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  readOnly
                  value={generatedLink}
                  className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-mono select-all focus:outline-none"
                />
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(generatedLink);
                    setCopied(true);
                    setTimeout(() => setCopied(false), 2000);
                  }}
                  className="p-2.5 bg-blue-600 text-white rounded-xl"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
                </button>
              </div>
              <div className="flex justify-end pt-2">
                <button
                  onClick={() => setLinkModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-white text-xs font-semibold rounded-xl"
                >
                  Listo
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
