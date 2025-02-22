import spacy
from typing import Dict, List, Optional, Tuple
import re
from collections import Counter
import logging
import html
import docx
import PyPDF2
import io
import time
from django.utils.timezone import now

logger = logging.getLogger(__name__)

class DocumentConverter:
    @staticmethod
    def extract_text(file) -> Tuple[str, str]:
        """Extract text from various file formats"""
        filename = file.name.lower()
        content = ""
         
        if filename.endswith('.txt'):
            content = file.read().decode('utf-8')
        elif filename.endswith('.docx'):
            doc = docx.Document(file)
            content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            content = "\n".join([page.extract_text() for page in pdf_reader.pages])
         
        return content, filename

class DocumentProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError as e:
            logger.error(f"Failed to load spaCy model: {str(e)}")
            raise Exception("NLP model initialization failed")
        
        self.filler_words = set([
            "very", "really", "basically", "actually", "literally",
            "just", "quite", "rather", "somewhat", "simply",
            "in my opinion", "needless to say", "as a matter of fact"
        ])
        
        self.grammar_patterns = [
            (r"i(?![a-zA-Z])", "I"),  # Capitalize 'I'
            (r"(?<=\.)\s*[a-z]", lambda m: m.group().upper()),  # Capitalize after period
            (r"\s+,", ","),  # Remove space before comma
            (r"\s+\.", "."),  # Remove space before period
        ]
    
    def process_document(self, text: str) -> Dict:
        """Main method to process document and generate improvements"""
        try:
            start_time = time.time()
            doc = self.nlp(text)
            
            grammar_suggestions = self._check_grammar(doc)
            style_suggestions = self._check_style(doc)
            clarity_improvements = self._improve_clarity(doc)
            
            # Generate improved text
            improved_text = self._generate_improved_text(text, doc)
            
            results = {
                'original_text': text,
                'improved_text': improved_text,
                'grammar_suggestions': grammar_suggestions,
                'style_suggestions': style_suggestions,
                'clarity_improvements': clarity_improvements,
                'tone_analysis': self._analyze_tone(doc),
                'consistency_score': self._check_consistency(doc),
                'document_stats': self._generate_stats(doc),
                'highlighted_html': self._generate_highlighted_text(text, doc),
                'processing_time': time.time() - start_time
            }
            
            return results
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    def process_file(self, file) -> Dict:
        """Process document from uploaded file"""
        try:
            # Use the DocumentConverter class to extract text
            start_time = time.time()
            content, filename = DocumentConverter.extract_text(file)
            
            # Now process the extracted text
            results = self.process_document(content)
            
            # Add file metadata to results
            results['file_info'] = {
                'filename': filename,
                'file_type': filename.split('.')[-1],
                'processed_at': now(),
                'extraction_time': time.time() - start_time
            }
            
            return results
        except Exception as e:
            logger.error(f"Error processing file {file.name}: {str(e)}")
            raise
    
    def _generate_improved_text(self, original_text: str, doc) -> str:
        """Generate improved version of the text based on suggestions"""
        # Get all suggestions
        grammar_suggestions = self._check_grammar(doc)
        style_suggestions = self._check_style(doc)
        clarity_improvements = self._improve_clarity(doc)
        
        # Combine all changes
        all_changes = []
        for suggestion in grammar_suggestions + style_suggestions + clarity_improvements:
            if 'position' in suggestion and 'suggestion' in suggestion:
                all_changes.append({
                    'start': suggestion['position']['start'],
                    'end': suggestion['position']['end'],
                    'original': suggestion['original'],
                    'replacement': self._get_replacement_text(suggestion),
                    'type': suggestion['type']
                })
        
        # Sort changes by position (from end to start to avoid offset issues)
        all_changes.sort(key=lambda x: x['start'], reverse=True)
        
        # Apply changes
        improved = original_text
        for change in all_changes:
            if change['type'] == 'grammar' and 'pattern_match' in change.get('subtype', ''):
                # For grammar pattern matches, apply the direct replacement
                improved = improved[:change['start']] + change['replacement'] + improved[change['end']:]
            elif change['type'] == 'style' and change.get('subtype') == 'passive_voice':
                # Skip passive voice suggestions as they require manual rewording
                continue
            elif change['type'] == 'style' and change.get('subtype') == 'sentence_length':
                # Skip sentence length suggestions as they require manual rewording
                continue
            elif change['type'] == 'style' and change.get('subtype') == 'filler_words':
                # Remove filler words
                for filler in self.filler_words:
                    improved = re.sub(r'\b' + re.escape(filler) + r'\b', '', improved)
            
        return improved
    
    def _get_replacement_text(self, suggestion: Dict) -> str:
        """Get replacement text based on suggestion type"""
        if suggestion['type'] == 'grammar' and suggestion.get('subtype') == 'pattern_match':
            return suggestion['suggestion']
        elif suggestion['type'] == 'style' and suggestion.get('subtype') == 'filler_words':
            # For filler words, just return empty string to remove them
            return ""
        else:
            # For other suggestions, return original text as we can't automatically fix them
            return suggestion['original']
    
    def _check_grammar(self, doc) -> List[Dict]:
        """Check for grammar issues"""
        suggestions = []
        
        for sent in doc.sents:
            # Subject-verb agreement
            for token in sent:
                if token.dep_ == "nsubj":
                    verb = next((t for t in token.head.rights if t.pos_ == "VERB"), None)
                    if verb and not self._check_agreement(token, verb):
                        suggestions.append({
                            'type': 'grammar',
                            'subtype': 'subject_verb_agreement',
                            'original': sent.text,
                            'suggestion': f"Check agreement between '{token.text}' and '{verb.text}'",
                            'position': {'start': sent.start_char, 'end': sent.end_char},
                            'confidence': 0.9
                        })
            
            # Apply grammar patterns
            for pattern, replacement in self.grammar_patterns:
                matches = list(re.finditer(pattern, sent.text))
                for match in matches:
                    corrected = replacement(match) if callable(replacement) else replacement
                    suggestions.append({
                        'type': 'grammar',
                        'subtype': 'pattern_match',
                        'original': match.group(),
                        'suggestion': corrected,
                        'position': {
                            'start': sent.start_char + match.start(),
                            'end': sent.start_char + match.end()
                        },
                        'confidence': 0.85
                    })
        
        return suggestions
    
    def _check_style(self, doc) -> List[Dict]:
        """Check for style improvements"""
        suggestions = []
        
        for sent in doc.sents:
            # Check sentence length
            if len(sent) > 40:
                suggestions.append({
                    'type': 'style',
                    'subtype': 'sentence_length',
                    'original': sent.text,
                    'suggestion': "Consider breaking this long sentence into smaller ones",
                    'position': {'start': sent.start_char, 'end': sent.end_char},
                    'confidence': 0.7
                })
            
            # Check for passive voice
            if any(token.dep_ == "nsubjpass" for token in sent):
                suggestions.append({
                    'type': 'style',
                    'subtype': 'passive_voice',
                    'original': sent.text,
                    'suggestion': "Consider using active voice",
                    'position': {'start': sent.start_char, 'end': sent.end_char},
                    'confidence': 0.8
                })
            
            # Check for filler words
            fillers = [token.text for token in sent if token.text.lower() in self.filler_words]
            if fillers:
                suggestions.append({
                    'type': 'style',
                    'subtype': 'filler_words',
                    'original': sent.text,
                    'suggestion': f"Consider removing filler words: {', '.join(fillers)}",
                    'position': {'start': sent.start_char, 'end': sent.end_char},
                    'confidence': 0.75
                })
        
        return suggestions
    
    def _improve_clarity(self, doc) -> List[Dict]:
        """Generate clarity improvement suggestions"""
        suggestions = []
        
        # Check for repeated words in close proximity
        word_positions = {}
        for token in doc:
            if token.is_alpha and not token.is_stop:
                if token.lower_ not in word_positions:
                    word_positions[token.lower_] = []
                word_positions[token.lower_].append(token.i)
        
        for word, positions in word_positions.items():
            if len(positions) > 1:
                for i in range(len(positions) - 1):
                    if positions[i + 1] - positions[i] < 5:
                        span = doc[positions[i]:positions[i+1]+1]
                        suggestions.append({
                            'type': 'clarity',
                            'subtype': 'word_repetition',
                            'original': span.text,
                            'suggestion': f"Consider using a synonym for repeated word '{word}'",
                            'position': {'start': span.start_char, 'end': span.end_char},
                            'confidence': 0.7
                        })
        
        return suggestions
    
    def _analyze_tone(self, doc) -> Dict:
        """Analyze document tone"""
        # Simple tone analysis based on key indicators
        tone_indicators = {
            'formal': set(['therefore', 'moreover', 'consequently', 'thus']),
            'informal': set(['pretty', 'kind of', 'sort of', 'thing']),
            'positive': set(['good', 'great', 'excellent', 'beneficial']),
            'negative': set(['bad', 'poor', 'inadequate', 'harmful'])
        }
        
        tone_scores = {tone: 0 for tone in tone_indicators}
        for token in doc:
            for tone, indicators in tone_indicators.items():
                if token.text.lower() in indicators:
                    tone_scores[tone] += 1
        
        return {
            'tone_scores': tone_scores,
            'dominant_tone': max(tone_scores.items(), key=lambda x: x[1])[0],
            'confidence': 0.7
        }
    
    def _check_consistency(self, doc) -> float:
        """Check document consistency"""
        # Check terminology consistency
        terms = Counter()
        for token in doc:
            if token.is_alpha and not token.is_stop:
                terms[token.lower_] += 1
        
        # Calculate consistency score
        total_terms = sum(terms.values())
        unique_terms = len(terms)
        consistency_score = 1 - (unique_terms / total_terms if total_terms > 0 else 0)
        
        return consistency_score
    
    def _generate_stats(self, doc) -> Dict:
        """Generate comprehensive document statistics"""
        
        # Calculate paragraphs (split by double newlines)
        text = doc.text
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        num_paragraphs = len(paragraphs) if paragraphs else 1  # Minimum 1 paragraph
        
        # Count words (excluding punctuation)
        words = [token for token in doc if not token.is_punct]
        num_words = len(words)
        
        # Count sentences
        sentences = list(doc.sents)
        num_sentences = len(sentences)
        
        # Calculate average sentence length
        avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
        
        # Calculate readability score (using Flesch-Kincaid formula)
        syllables = sum([len([y for y in token.text if y.lower() in 'aeiou']) 
                        for token in words])
        readability_score = 206.835 - 1.015 * (num_words / num_sentences) - \
                        84.6 * (syllables / num_words) if num_words > 0 else 0
        
        # Calculate vocabulary diversity (unique words / total words)
        unique_words = len(set([token.text.lower() for token in words]))
        vocabulary_diversity = unique_words / num_words if num_words > 0 else 0
        
        # Analyze tone confidence and consistency
        tone_confidence = 0.7  # Default confidence score
        consistency_details = {
            'repeated_terms': self._find_repeated_terms(doc),
            'style_consistency': self._check_style_consistency(doc)
        }
        
        return {
            'num_paragraphs': num_paragraphs,
            'num_sentences': num_sentences,
            'num_words': num_words,
            'avg_sentence_length': avg_sentence_length,
            'readability_score': readability_score,
            'vocabulary_diversity': vocabulary_diversity,
            'tone_confidence': tone_confidence,
            'consistency_details': consistency_details
        }

    def _find_repeated_terms(self, doc) -> Dict:
        """Find frequently repeated terms in the document"""
        terms = {}
        for token in doc:
            if token.is_alpha and not token.is_stop:
                term = token.text.lower()
                if term not in terms:
                    terms[term] = 0
                terms[term] += 1
        
        return {term: count for term, count in terms.items() if count > 3}

    def _check_style_consistency(self, doc) -> Dict:
        """Check consistency in writing style"""
        return {
            'sentence_length_variance': self._calculate_sentence_length_variance(doc),
            'formality_consistency': self._check_formality_consistency(doc)
        }

    def _calculate_sentence_length_variance(self, doc) -> float:
        """Calculate variance in sentence lengths"""
        sentence_lengths = [len(sent) for sent in doc.sents]
        if not sentence_lengths:
            return 0
        mean = sum(sentence_lengths) / len(sentence_lengths)
        variance = sum((x - mean) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        return variance

    def _check_formality_consistency(self, doc) -> float:
        """Check consistency in formal vs informal language"""
        formal_markers = set(['therefore', 'consequently', 'furthermore', 'moreover'])
        informal_markers = set(['pretty', 'kind of', 'sort of', 'basically'])
        
        formal_count = 0
        informal_count = 0
        
        for token in doc:
            if token.text.lower() in formal_markers:
                formal_count += 1
            elif token.text.lower() in informal_markers:
                informal_count += 1
        
        total = formal_count + informal_count
        if total == 0:
            return 1.0  # Perfect consistency if no markers found
        
        # Return ratio of dominant style
        return max(formal_count, informal_count) / total
        
    def _check_agreement(self, subject: spacy.tokens.Token, verb: spacy.tokens.Token) -> bool:
        """Check if subject and verb agree in number"""
        subject_number = "singular" if subject.tag_ in ["NN", "NNP"] else "plural"
        verb_number = "singular" if verb.tag_ == "VBZ" else "plural"
        return subject_number == verb_number
    
    def _generate_highlighted_text(self, original_text: str, doc) -> str:
        """Generate HTML with highlighted corrections and suggestions"""
        # Collect all corrections and suggestions
        all_changes = []
        
        # Add grammar suggestions
        grammar_suggestions = self._check_grammar(doc)
        for suggestion in grammar_suggestions:
            all_changes.append({
                'start': suggestion['position']['start'],
                'end': suggestion['position']['end'],
                'original': suggestion['original'],
                'suggestion': suggestion['suggestion'],
                'type': suggestion['type'],
                'subtype': suggestion.get('subtype', '')
            })
        
        # Add style suggestions
        style_suggestions = self._check_style(doc)
        for suggestion in style_suggestions:
            all_changes.append({
                'start': suggestion['position']['start'],
                'end': suggestion['position']['end'],
                'original': suggestion['original'],
                'suggestion': suggestion['suggestion'],
                'type': suggestion['type'],
                'subtype': suggestion.get('subtype', '')
            })
        
        # Add clarity improvements
        clarity_improvements = self._improve_clarity(doc)
        for improvement in clarity_improvements:
            all_changes.append({
                'start': improvement['position']['start'],
                'end': improvement['position']['end'],
                'original': improvement['original'],
                'suggestion': improvement['suggestion'],
                'type': improvement['type'],
                'subtype': improvement.get('subtype', '')
            })
        
        # Sort changes by position
        all_changes.sort(key=lambda x: x['start'])
        
        # Generate HTML with highlighted changes
        html_parts = []
        last_pos = 0
        
        for change in all_changes:
            # Add text between last change and current change
            if change['start'] > last_pos:
                html_parts.append(html.escape(original_text[last_pos:change['start']]))
            
            # Determine highlight color and tooltip based on change type
            highlight_color = self._get_highlight_color(change['type'], change['subtype'])
            tooltip_text = change['suggestion']
            
            # Add highlighted text
            highlighted_text = self._format_highlighted_text(change)
            html_parts.append(f'<span style="background-color: {highlight_color};" title="{html.escape(tooltip_text)}">{highlighted_text}</span>')
            
            last_pos = change['end']
        
        # Add remaining text
        if last_pos < len(original_text):
            html_parts.append(html.escape(original_text[last_pos:]))
        
        # Convert newlines to <br> tags
        html_content = ''.join(html_parts).replace('\n', '<br>')
        
        # Wrap in HTML document
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Document with Highlighted Corrections</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
        .document-container {{ max-width: 800px; margin: 0 auto; }}
        .legend {{ margin-bottom: 20px; border: 1px solid #ddd; padding: 10px; }}
        .legend-item {{ display: inline-block; margin-right: 15px; }}
        .legend-color {{ display: inline-block; width: 15px; height: 15px; margin-right: 5px; vertical-align: middle; }}
    </style>
</head>
<body>
    <div class="document-container">
        <h1>Processed Document with Suggestions</h1>
        
        <div class="legend">
            <h3>Legend:</h3>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ffcccc;"></span>
                Grammar Issues
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ffffcc;"></span>
                Style Suggestions
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #ccffcc;"></span>
                Clarity Improvements
            </div>
            <div class="legend-item">
                <span class="legend-color" style="background-color: #e6e6ff;"></span>
                Punctuation Issues
            </div>
        </div>
        
        <div class="document-text">
            {html_content}
        </div>
    </div>
</body>
</html>"""
    
    def _get_highlight_color(self, change_type: str, change_subtype: str) -> str:
        """Determine highlight color based on suggestion type"""
        if change_type == 'grammar':
            if change_subtype == 'pattern_match' and 'comma' in change_subtype:
                return '#e6e6ff'  # Light blue for comma issues
            return '#ffcccc'  # Light red for grammar issues
        elif change_type == 'style':
            return '#ffffcc'  # Light yellow for style issues
        elif change_type == 'clarity':
            return '#ccffcc'  # Light green for clarity improvements
        else:
            return '#f2f2f2'  # Light gray for other issues
    
    def _format_highlighted_text(self, change: Dict) -> str:
        """Format highlighted text with strike-through for original and suggestion"""
        original_text = html.escape(change['original'])
        
        if change['type'] == 'grammar' and change['subtype'] == 'pattern_match':
            # For pattern matches, show the corrected text
            if change['suggestion'] == ',':
                # Special handling for comma suggestions - visually indicate the added comma
                return f'<span style="text-decoration: line-through;">{original_text}</span> <span style="color: green; font-weight: bold;">{html.escape(change["suggestion"])}</span>'
            else:
                return f'<span style="text-decoration: line-through;">{original_text}</span> <span style="color: green; font-weight: bold;">{html.escape(change["suggestion"])}</span>'
        else:
            # For other suggestions, just highlight the text
            return original_text

# Usage example:
def process_uploaded_document(file):
    """Main function to handle document processing from upload to results"""
    processor = DocumentProcessor()
    try:
        # This now properly uses the DocumentConverter via the process_file method
        results = processor.process_file(file)
        return results
    except Exception as e:
        logger.error(f"Failed to process document: {str(e)}")
        raise