import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Paper,
  Typography,
  Box
} from '@mui/material';

const DocumentPreview = ({ open, onClose, content }) => {
  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '80vh'
        }
      }}
    >
      <DialogTitle>
        Document Preview
      </DialogTitle>
      <DialogContent>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            minHeight: '60vh',
            bgcolor: '#fff',
            border: '1px solid #e0e0e0',
            width: '21cm', // A4 width
            mx: 'auto',
            '@media print': {
              width: '21cm',
              height: '29.7cm', // A4 height
              margin: 0,
              padding: '2.54cm', // 1-inch margins
              boxShadow: 'none',
              border: 'none'
            }
          }}
        >
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            gap: 2
          }}>
            {/* Header with organization logo and info */}
            <Box sx={{
              display: 'flex',
              justifyContent: 'space-between',
              mb: 4
            }}>
              <Box>
                <Typography variant="h6" sx={{ color: 'primary.main' }}>
                  Organization Name
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  123 Business Street
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  City, State 12345
                </Typography>
              </Box>
              <Box sx={{
                width: 100,
                height: 50,
                bgcolor: 'grey.200',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Typography variant="caption">Logo</Typography>
              </Box>
            </Box>

            {/* Document content */}
            <Typography
              sx={{
                whiteSpace: 'pre-wrap',
                fontFamily: 'Times New Roman',
                fontSize: '12pt',
                lineHeight: 1.5
              }}
            >
              {content}
            </Typography>

            {/* Footer */}
            <Box sx={{
              mt: 'auto',
              pt: 2,
              borderTop: '1px solid',
              borderColor: 'grey.300',
              textAlign: 'center'
            }}>
              <Typography variant="caption" color="textSecondary">
                Page 1 of 1 | Generated on {new Date().toLocaleDateString()}
              </Typography>
            </Box>
          </Box>
        </Paper>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => window.print()} color="primary">
          Print
        </Button>
        <Button onClick={onClose}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DocumentPreview;