import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';
import { resolveMediaUrl } from '../services/api';

interface MediaViewerProps {
  content: string;
  className?: string;
  isAudioDestino?: boolean;
  altText?: string;
  autoPlayOnClick?: boolean;
}

export const isAudioUrl = (url: string): boolean => {
  if (!url) return false;
  const cleanUrl = url.split('?')[0].toLowerCase();
  return (
    cleanUrl.endsWith('.mp3') ||
    cleanUrl.endsWith('.wav') ||
    cleanUrl.endsWith('.ogg') ||
    cleanUrl.endsWith('.m4a') ||
    cleanUrl.endsWith('.aac')
  );
};

export const isImageUrl = (url: string): boolean => {
  if (!url) return false;
  const cleanUrl = url.split('?')[0].toLowerCase();
  return (
    cleanUrl.endsWith('.png') ||
    cleanUrl.endsWith('.jpg') ||
    cleanUrl.endsWith('.jpeg') ||
    cleanUrl.endsWith('.svg') ||
    cleanUrl.endsWith('.webp') ||
    cleanUrl.endsWith('.gif')
  );
};

export const MediaViewer: React.FC<MediaViewerProps> = ({
  content,
  className = '',
  isAudioDestino = false,
  altText = 'Elemento',
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioError, setAudioError] = useState(false);

  const isAudio = isAudioDestino || isAudioUrl(content);
  const isImage = isImageUrl(content);

  const handlePlayAudio = (e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation();
    }
    if (!content) return;

    try {
      const resolved = resolveMediaUrl(content);
      const audio = new Audio(resolved);
      setIsPlaying(true);
      setAudioError(false);

      audio.play().catch((err) => {
        console.error('Error al reproducir audio:', err);
        setAudioError(true);
        setIsPlaying(false);
      });

      audio.onended = () => setIsPlaying(false);
      audio.onerror = () => {
        setAudioError(true);
        setIsPlaying(false);
      };
    } catch {
      setAudioError(true);
      setIsPlaying(false);
    }
  };

  if (isAudio) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <button
          type="button"
          onClick={handlePlayAudio}
          className={`p-2.5 rounded-full transition-all flex items-center justify-center shadow-sm ${
            isPlaying
              ? 'bg-blue-600 text-white animate-pulse ring-4 ring-blue-200'
              : audioError
              ? 'bg-red-100 text-red-600'
              : 'bg-blue-50 text-blue-600 hover:bg-blue-100 hover:scale-105'
          }`}
          title={isPlaying ? 'Reproduciendo sonido...' : 'Reproducir sonido'}
        >
          {audioError ? <VolumeX className="w-5 h-5" /> : <Volume2 className="w-5 h-5" />}
        </button>
        <div className="flex flex-col text-left">
          <span className="text-xs font-bold text-slate-700">
            {isPlaying ? 'Escuchando...' : 'Sonido'}
          </span>
          <span className="text-[10px] text-slate-400 font-mono truncate max-w-[140px]">
            {content.split('/').pop() || 'audio'}
          </span>
        </div>
      </div>
    );
  }

  if (isImage) {
    const resolvedImg = resolveMediaUrl(content);
    return (
      <img
        src={resolvedImg}
        alt={altText}
        className={`max-h-16 max-w-24 object-contain rounded-lg border border-slate-200 bg-white ${className}`}
        onError={(e) => {
          // Fallback a texto si falla la carga de la imagen
          (e.target as HTMLElement).style.display = 'none';
        }}
      />
    );
  }

  return <span className={`truncate ${className}`}>{content}</span>;
};
