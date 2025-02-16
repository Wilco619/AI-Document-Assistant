import spacy
from typing import Dict, List, Optional
import re
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_lg")
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
            doc = self.nlp(text)
            
            results = {
                'grammar_suggestions': self._check_grammar(doc),
                'style_suggestions': self._check_style(doc),
                'clarity_improvements': self._improve_clarity(doc),
                'tone_analysis': self._analyze_tone(doc),
                'consistency_score': self._check_consistency(doc),
                'document_stats': self._generate_stats(doc)
            }
            
            return results
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
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
        # This is a simple implementation - you might want to enhance it
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