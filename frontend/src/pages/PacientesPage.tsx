import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { getPacientes, createPaciente, updatePaciente, deletePaciente } from '../services/api';
import { Paciente } from '../types';
import { UserPlus, Edit2, Trash2, X, AlertCircle, ChevronLeft, ChevronRight, BarChart2 } from 'lucide-react';


export const PacientesPage: React.FC = () => {
  const navigate = useNavigate();
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [size] = useState(10);
  const [loading, setLoading] = useState(true);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPaciente, setEditingPaciente] = useState<Paciente | null>(null);
  const [apodo, setApodo] = useState('');
  const [edad, setEdad] = useState<string>('');
  const [modalError, setModalError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Confirmation Delete Modal
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchPacientes = async () => {
    setLoading(true);
    try {
      const data = await getPacientes(page, size);
      setPacientes(data.items);
      setTotal(data.total);
    } catch (err: any) {
      console.error('Error al cargar pacientes', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPacientes();
  }, [page]);

  const openCreateModal = () => {
    setEditingPaciente(null);
    setApodo('');
    setEdad('');
    setModalError('');
    setIsModalOpen(true);
  };

  const openEditModal = (paciente: Paciente) => {
    setEditingPaciente(paciente);
    setApodo(paciente.apodo);
    setEdad(paciente.edad !== null && paciente.edad !== undefined ? String(paciente.edad) : '');
    setModalError('');
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apodo.trim()) {
      setModalError('El seudónimo es requerido');
      return;
    }

    setSubmitting(true);
    setModalError('');
    try {
      const payload = {
        apodo: apodo.trim(),
        edad: edad ? parseInt(edad, 10) : null,
      };

      if (editingPaciente) {
        await updatePaciente(editingPaciente.id, payload);
      } else {
        await createPaciente(payload);
      }

      setIsModalOpen(false);
      fetchPacientes();
    } catch (err: any) {
      setModalError(err.response?.data?.detail || 'Error al guardar el paciente');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deletePaciente(id);
      setDeletingId(null);
      fetchPacientes();
    } catch (err: any) {
      alert('Error al eliminar paciente: ' + (err.response?.data?.detail || 'Error desconocido'));
    }
  };

  const totalPages = Math.ceil(total / size) || 1;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200/80">
          <div>
            <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Mis Pacientes</h2>
            <p className="text-sm text-slate-500 mt-1">
              Gestiona los perfiles y fichas de estimulación de los niños a tu cargo.
            </p>
          </div>
          <button
            onClick={openCreateModal}
            className="inline-flex items-center justify-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl shadow-md shadow-blue-600/20 transition duration-150 gap-2"
          >
            <UserPlus className="w-5 h-5" />
            <span>+ Nuevo Paciente</span>
          </button>
        </div>

        {/* Table Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-xs font-bold text-slate-500 uppercase tracking-wider">
                  <th className="px-6 py-4">Seudónimo</th>
                  <th className="px-6 py-4">Edad</th>
                  <th className="px-6 py-4">Última Sesión</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="text-center py-12 text-slate-400">
                      Cargando pacientes...
                    </td>
                  </tr>
                ) : pacientes.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-12 text-slate-400">
                      No tienes pacientes registrados aún. Haz clic en "+ Nuevo Paciente" para comenzar.
                    </td>
                  </tr>
                ) : (
                  pacientes.map((p) => {
                    const isEliminado = !!p.eliminado_en;
                    return (
                      <tr key={p.id} className="hover:bg-slate-50/70 transition">
                        <td className="px-6 py-4 font-semibold text-slate-800">
                          {p.apodo}
                        </td>
                        <td className="px-6 py-4 text-slate-600">
                          {p.edad ? `${p.edad} años` : 'Sin especificar'}
                        </td>
                        <td className="px-6 py-4 text-slate-500">
                          {p.ultima_sesion
                            ? new Date(p.ultima_sesion).toLocaleDateString()
                            : 'Sin sesiones aún'}
                        </td>
                        <td className="px-6 py-4">
                          <span
                            className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                              isEliminado
                                ? 'bg-red-50 text-red-700 border border-red-200'
                                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            }`}
                          >
                            {isEliminado ? 'Eliminado' : 'Activo'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right space-x-2">
                          <button
                            onClick={() => navigate(`/pacientes/${p.id}/metricas`)}
                            className="p-1.5 text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition"
                            title="Ver métricas y evolución"
                          >
                            <BarChart2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => openEditModal(p)}
                            className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition"
                            title="Editar paciente"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setDeletingId(p.id)}
                            className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                            title="Eliminar paciente"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Página {page} de {totalPages} ({total} pacientes en total)
              </span>
              <div className="flex items-center space-x-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage(page - 1)}
                  className="p-2 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition"
                >
                  <ChevronLeft className="w-4 h-4 text-slate-600" />
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage(page + 1)}
                  className="p-2 border border-slate-200 rounded-lg disabled:opacity-40 hover:bg-slate-50 transition"
                >
                  <ChevronRight className="w-4 h-4 text-slate-600" />
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Modal Crear / Editar */}
        {isModalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100">
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <h3 className="text-lg font-bold text-slate-800">
                  {editingPaciente ? 'Editar Paciente' : 'Nuevo Paciente'}
                </h3>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {modalError && (
                <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{modalError}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-5 space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Seudónimo / Apodo *
                  </label>
                  <input
                    type="text"
                    required
                    value={apodo}
                    onChange={(e) => setApodo(e.target.value)}
                    placeholder="Ej: Mateo C."
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  />
                  <p className="text-xs text-slate-400 mt-1">Para resguardar la privacidad del menor.</p>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                    Edad (Años)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    value={edad}
                    onChange={(e) => setEdad(e.target.value)}
                    placeholder="Ej: 7"
                    className="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
                  />
                </div>

                <div className="pt-3 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2.5 border border-slate-200 text-slate-600 font-semibold text-sm rounded-xl hover:bg-slate-50 transition"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm rounded-xl shadow-md shadow-blue-600/20 transition disabled:opacity-50"
                  >
                    {submitting ? 'Guardando...' : editingPaciente ? 'Guardar Cambios' : 'Crear Paciente'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal Confirmación Eliminación */}
        {deletingId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-100 text-center">
              <div className="w-12 h-12 rounded-full bg-red-100 text-red-600 flex items-center justify-center mx-auto mb-4">
                <Trash2 className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">¿Eliminar paciente?</h3>
              <p className="text-sm text-slate-500 mb-6">
                El paciente pasará a estado inactivo (soft delete). Sus sesiones y actividades asociadas se preservarán.
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
                  Confirmar Eliminación
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
