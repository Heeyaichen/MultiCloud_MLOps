import React from 'react';
import { Box, Paper, Typography } from '@mui/material';

interface VideoPlayerProps {
  videoUrl: string;
  title?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl, title }) => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      {title && (
        <Typography variant="h6" gutterBottom>
          {title}
        </Typography>
      )}
      <Box
        component="video"
        controls
        sx={{
          width: '100%',
          maxHeight: '500px',
          backgroundColor: '#000',
          borderRadius: 1,
        }}
      >
        <source src={videoUrl} type="video/mp4" />
        <source src={videoUrl} type="video/quicktime" />
        <source src={videoUrl} type="video/x-msvideo" />
        Your browser does not support the video tag.
      </Box>
    </Paper>
  );
};

export default VideoPlayer;
