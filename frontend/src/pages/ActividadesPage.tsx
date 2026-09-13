import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { getActividades, deleteActividad, generarEnlace } from '../services/api';
import { Actividad } from '../types';
import {
  Plus,
  Edit2,
  Trash2,
  Link as LinkIcon,
  Copy,
  Check,
  Calendar,
  X,
  Layers,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

export const ActividadesPage: React.FC = () => {
  const [actividades, setActividades] = useState<Actividad[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Modal Enlace
  const [linkModalOpen, setLinkModalOpen] = useState(false);
  const [currentLink, setCurrentLink] = useState('');
  const [linkExpira, setLinkExpira] = useState('');
  const [copied, setCopied] = useState(false);

  // Modal Eliminar
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchActividades = async () => {
    setLoading(true);
    try {
      const data = await getActividades();
      setActividades(data.items);
    } catch (err) {
      console.error('Error al cargar actividades', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActividades();
  }, []);

  const handleGenerateLink = async (id: string) => {
    try {
      const data = await generarEnlace(id);
      const origin = window.location.origin;
      setCurrentLink(`${origin}${data.url_completa}`);
      setLinkExpira(new Date(data.expira_en).toLocaleDateString());
      setCopied(false);
      setLinkModalOpen(true);
    } catch (err: any) {
      alert('Error al generar enlace: ' + (err.response?.data?.detail || 'Error desconocido'));
    }
  };


  const handleCopyLink = () => {
    navigator.clipboard.writeText(currentLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteActividad(id);
      setDeletingId(null);
      fetchActividades();
    } catch (err: any) {
      alert('Error al eliminar actividad');
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200/80">
          <div>
            <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Plantillas de Ejercicios</h2>
            <p className="text-sm text-slate-500 mt-1">
              Diseña, personaliza y comparte actividades cognitivas de asociación (Plantilla 1).
            </p>
          </div>
          <button
            onClick={() => navigate('/actividades/nueva')}
            className="inline-flex items-center justify-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md shadow-blue-600/20 transition duration-150 gap-2"
          >
            <Plus className="w-5 h-5" />
            <span>+ Nueva Actividad</span>
          </button>
        </div>

        {/* Grid de Actividades */}
        {loading ? (
          <div className="bg-white rounded-2xl p-12 text-center text-slate-400 border border-slate-200/80">
            Cargando actividades...
          </div>
        ) : actividades.length === 0 ? (
          <div className="bg-white rounded-2xl p-12 text-center text-slate-400 border border-slate-200/80 space-y-3">
            <Layers className="w-12 h-12 mx-auto text-slate-300" />
            <h3 className="text-lg font-bold text-slate-700">No hay actividades creadas aún</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Crea tu primer configurador de asociación con imágenes, sonidos o texto adaptado a tus pacientes.
            </p>
            <button
              onClick={() => navigate('/actividades/nueva')}
              className="mt-2 px-4 py-2 bg-blue-600 text-white font-semibold rounded-xl text-sm hover:bg-blue-700 transition"
            >
              Crear Actividad Ahora
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {actividades.map((act) => (
              <div
                key={act.id}
                className="bg-white rounded-2xl border border-slate-200/80 shadow-sm hover:shadow-md transition flex flex-col justify-between overflow-hidden group"
              >
                <div className="p-6 space-y-4">
                  <div className="flex items-start justify-between gap-3">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200 uppercase tracking-wide">
                      {act.modo}
                    </span>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                        act.activa
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-600'
                      }`}
                    >
                      {act.activa ? 'Activa' : 'Pausada'}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-lg font-bold text-slate-800 group-hover:text-blue-600 transition line-clamp-1">
                      {act.titulo}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                      {act.descripcion || 'Sin descripción adicional.'}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                      {act.pares?.length || 0} pares asociados
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5 text-slate-400" />
                      {act.creado_en ? new Date(act.creado_en).toLocaleDateString() : ''}
                    </span>
                  </div>
                </div>

                {/* Acciones de la Tarjeta */}
                <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => navigate(`/actividades/${act.id}/editar`)}
                      className="p-1.5 text-slate-600 hover:text-blue-600 hover:bg-white rounded-lg transition"
                      title="Editar plantilla"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeletingId(act.id)}
                      className="p-1.5 text-slate-600 hover:text-red-600 hover:bg-white rounded-lg transition"
                      title="Eliminar plantilla"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <button
                    onClick={() => handleGenerateLink(act.id)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs rounded-xl shadow-sm transition"
                  >
                    <LinkIcon className="w-3.5 h-3.5" />
                    <span>Generar Enlace</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal Enlace Generado */}
        {linkModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <div className="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
                    <LinkIcon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-800">Enlace Único de Actividad</h3>
                    <p className="text-xs text-slate-400">Válido para juego infantil sin login</p>
                  </div>
                </div>
                <button
                  onClick={() => setLinkModalOpen(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-bold text-slate-600 uppercase tracking-wider">
                  URL de Acceso
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    readOnly
                    value={currentLink}
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-700 font-mono select-all focus:outline-none"
                  />
                  <button
                    onClick={handleCopyLink}
                    className="p-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm transition flex-shrink-0"
                    title="Copiar al portapapeles"
                  >
                    {copied ? <Check className="w-4 h-4 text-emerald-300" /> : <Copy className="w-4 h-4" />}
                  </button>
                </div>
                {copied && (
                  <p className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                    <Check className="w-3.5 h-3.5" /> ¡Enlace copiado al portapapeles!
                  </p>
                )}
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 space-y-1">
                <p>• Expira el: <strong className="text-slate-700">{linkExpira}</strong> (7 días)</p>
                <p>• El paciente podrá jugar directamente sin usuario ni contraseña.</p>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <a
                  href={currentLink}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 border border-slate-200 text-slate-700 text-xs font-semibold rounded-xl hover:bg-slate-50 transition"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> Probar en nueva pestaña
                </a>
                <button
                  onClick={() => setLinkModalOpen(false)}
                  className="px-4 py-2 bg-slate-800 text-white text-xs font-semibold rounded-xl hover:bg-slate-900 transition"
                >
                  Cerrar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Modal Eliminar */}
        {deletingId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 text-center">
              <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
                <Trash2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">¿Eliminar actividad?</h3>
              <p className="text-sm text-slate-500 mb-6">
                La actividad será desactivada y sus enlaces dejarán de funcionar.
              </p>
              <div className="flex justify-center gap-3">
                <button
                  onClick={() => setDeletingId(null)}
                  className="px-4 py-2.5 border border-slate-200 text-slate-600 font-semibold text-sm rounded-xl hover:bg-slate-50 transition"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => handleDelete(deletingId)}
                  className="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-red-600/20 transition"
                >
                  Confirmar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
