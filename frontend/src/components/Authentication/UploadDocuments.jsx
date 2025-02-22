import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Button,
  CircularProgress,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CardActions,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import api from '../../api';
import DocumentPreview from './DocumentPreview';

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [documentData, setDocumentData] = useState(null);
  const [improvedText, setImprovedText] = useState('');
  const [suggestions, setSuggestions] = useState({
    grammar: [],
    style: [],
    clarity: []
  });
  const [appliedSuggestions, setAppliedSuggestions] = useState([]);
  const [rejectedSuggestions, setRejectedSuggestions] = useState([]);
  const [exportAnchorEl, setExportAnchorEl] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'text/plain': ['.txt'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    onDrop: acceptedFiles => {
      setFile(acceptedFiles[0]);
    }
  });

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const { data } = await api.post('/api/list/processed-documents/', formData);
      setDocumentData(data);
      setImprovedText(data.improved_text);
      setSuggestions({
        grammar: formatSuggestions(data.grammar_suggestions),
        style: formatSuggestions(data.style_suggestions),
        clarity: formatSuggestions(data.clarity_improvements)
      });
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const formatSuggestions = (suggestionList) => {
    return suggestionList.map((suggestion, index) => ({
      id: index,
      text: formatSuggestionText(suggestion),
      original: suggestion.original || '',
      suggested: suggestion.suggestion || '',
      type: suggestion.type || 'general',
      position: suggestion.position || null,
      confidence: suggestion.confidence || null
    }));
  };

  const formatSuggestionText = (suggestion) => {
    if (typeof suggestion === 'string') return suggestion;
    
    return `${suggestion.type}: Change "${suggestion.original}" to "${suggestion.suggestion}"${
      suggestion.confidence ? ` (Confidence: ${Math.round(suggestion.confidence * 100)}%)` : ''
    }`;
  };

  const handleAcceptSuggestion = async (suggestion) => {
    setAppliedSuggestions([...appliedSuggestions, suggestion]);
    
    try {
      const { data } = await api.post(`/api/list/processed-documents/${documentData.id}/apply_suggestion/`, {
        documentId: documentData.id,
        suggestion: {
          type: suggestion.type,
          original: suggestion.original,
          suggested: suggestion.suggested,
          position: suggestion.position
        },
        action: 'accept'
      });
      
      setImprovedText(data.improved_text);
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
    }
  };

  const handleRejectSuggestion = (suggestion) => {
    setRejectedSuggestions([...rejectedSuggestions, suggestion]);
  };

  const handleExport = async (format) => {
    try {
      const response = await api.get(
        `/api/list/processed-documents/${documentData.id}/export/`,
        {
          format,
          appliedSuggestions,
          rejectedSuggestions
        },
        { responseType: 'blob' } // Ensure response is a file blob
      );
  
      // Create a Blob from the response data
      const blob = new Blob([response.data], {
        type:
          format === 'pdf'
            ? 'application/pdf'
            : format === 'docx'
            ? 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            : 'text/plain'
      });
  
      // Generate a URL for the Blob
      const url = window.URL.createObjectURL(blob);
  
      // Create a download link and trigger click
      const a = document.createElement('a');
      a.href = url;
      a.download = `processed-document.${format}`;
      document.body.appendChild(a);
      a.click();
  
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExportAnchorEl(null);
    }
  };
  

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Document Processing
      </Typography>

      <Box
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          transition: 'all 0.2s ease'
        }}
      >
        <input {...getInputProps()} />
        <Typography>
          {isDragActive ? 'Drop the file here...' : 'Drag & drop a file here, or click to select'}
        </Typography>
      </Box>

      {file && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle1">
            Selected File: {file.name}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={handleUpload}
            disabled={uploading}
            sx={{ mt: 1 }}
          >
            {uploading ? <CircularProgress size={24} /> : 'Process Document'}
          </Button>
        </Box>
      )}

      {documentData && (
        <Box sx={{ mt: 4 }}>
          <Grid container spacing={3}>
            {/* Original Text */}
            <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 300, overflow: 'hidden', position: 'relative' }}>
                <Typography variant="h6" gutterBottom>Original Text</Typography>
                <Box sx={{
                    height: '240px', // Fixed height for scrolling
                    overflowY: 'auto', // Enable vertical scrolling
                    overflowX: 'hidden',
                    pr: 1 // Prevent horizontal overflow
                }}>
                    <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                    {documentData.original_text}
                    </Typography>
                </Box>
                </Paper>
            </Grid>

            {/* Improved Text */}
            <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 300, overflow: 'hidden', position: 'relative' }}>
                <Typography variant="h6" gutterBottom>
                    Improved Text
                    <IconButton size="small" onClick={() => setPreviewOpen(true)} sx={{ ml: 1 }}>
                    <VisibilityIcon />
                    </IconButton>
                </Typography>
                <Box sx={{
                    height: '240px', 
                    overflowY: 'auto',
                    overflowX: 'hidden',
                    pr: 1
                }}>
                    <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                    {improvedText}
                    </Typography>
                </Box>
                </Paper>
            </Grid>
            </Grid>

            {/* Suggestions */}
            <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>
                Suggestions
            </Typography>
            <Box sx={{
                height: '300px', // Fixed height
                overflowY: 'auto', // Enable scrolling
                overflowX: 'hidden',
                pr: 1, // Prevent horizontal overflow
                border: '1px solid #ddd',
                borderRadius: 1,
                p: 2
            }}>
                {Object.entries(suggestions).map(([type, suggestionList]) => (
                <Box key={type} sx={{ mb: 3 }}>
                    <Typography variant="subtitle1" sx={{ textTransform: 'capitalize', mb: 1 }}>
                    {type} Suggestions
                    </Typography>
                    <Grid container spacing={2}>
                    {suggestionList.map((suggestion) => {
                        const isApplied = appliedSuggestions.some(s => s.id === suggestion.id);
                        const isRejected = rejectedSuggestions.some(s => s.id === suggestion.id);
                        
                        if (isRejected) return null;
                        
                        return (
                        <Grid item xs={12} key={suggestion.id}>
                            <Card>
                            <CardContent>
                                <Typography>{suggestion.text}</Typography>
                            </CardContent>
                            {!isApplied && (
                                <CardActions sx={{ justifyContent: 'flex-end' }}>
                                <IconButton color="success" onClick={() => handleAcceptSuggestion(suggestion)}>
                                    <CheckIcon />
                                </IconButton>
                                <IconButton color="error" onClick={() => handleRejectSuggestion(suggestion)}>
                                    <CloseIcon />
                                </IconButton>
                                </CardActions>
                            )}
                            </Card>
                        </Grid>
                        );
                    })}
                    </Grid>
                </Box>
                ))}
            </Box>
            </Box>


          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              endIcon={<DownloadIcon />}
              onClick={(e) => setExportAnchorEl(e.currentTarget)}
            >
              Export Document
            </Button>
            <Menu
              anchorEl={exportAnchorEl}
              open={Boolean(exportAnchorEl)}
              onClose={() => setExportAnchorEl(null)}
            >
              {['txt', 'pdf', 'docx'].map((format) => (
                <MenuItem key={format} onClick={() => handleExport(format)}>
                  Export as .{format}
                </MenuItem>
              ))}
            </Menu>
          </Box>
        </Box>
      )}

      <DocumentPreview
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        content={improvedText}
      />
    </Box>
  );
};

export default DocumentUpload;