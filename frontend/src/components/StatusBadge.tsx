import React from 'react';
import { Chip } from '@mui/material';
import {
  CheckCircle,
  Cancel,
  HourglassEmpty,
  RateReview,
  CloudUpload,
  Psychology,
} from '@mui/icons-material';
import { VideoStatus } from '../types';

interface StatusBadgeProps {
  status: VideoStatus;
  size?: 'small' | 'medium';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'medium' }) => {
  const getStatusConfig = (status: VideoStatus) => {
    switch (status) {
      case 'approved':
        return {
          label: 'Approved',
          color: 'success' as const,
          icon: <CheckCircle />,
        };
      case 'rejected':
        return {
          label: 'Rejected',
          color: 'error' as const,
          icon: <Cancel />,
        };
      case 'review':
        return {
          label: 'Pending Review',
          color: 'warning' as const,
          icon: <RateReview />,
        };
      case 'uploaded':
        return {
          label: 'Uploaded',
          color: 'info' as const,
          icon: <CloudUpload />,
        };
      case 'screened':
        return {
          label: 'Screened',
          color: 'info' as const,
          icon: <Psychology />,
        };
      case 'analyzed':
        return {
          label: 'Analyzed',
          color: 'info' as const,
          icon: <Psychology />,
        };
      case 'processing':
        return {
          label: 'Processing',
          color: 'default' as const,
          icon: <HourglassEmpty />,
        };
      default:
        return {
          label: status,
          color: 'default' as const,
          icon: <HourglassEmpty />,
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <Chip
      label={config.label}
      color={config.color}
      size={size}
      icon={config.icon}
      sx={{ fontWeight: 500 }}
    />
  );
};

export default StatusBadge;
