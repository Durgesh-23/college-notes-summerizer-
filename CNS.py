import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import re
from collections import Counter
import math

class NoteSummarizer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("College Note Summarizer")
        self.root.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="College Note Summarizer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Input section
        ttk.Label(main_frame, text="Input Notes:").grid(row=1, column=0, sticky=tk.W)
        
        # File load button
        load_btn = ttk.Button(main_frame, text="Load from File", 
                             command=self.load_file)
        load_btn.grid(row=1, column=2, sticky=tk.E)
        
        # Input text area
        self.input_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.input_text.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                            pady=(5, 10))
        
        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Summary method selection
        ttk.Label(options_frame, text="Summary Method:").grid(row=0, column=0, sticky=tk.W)
        self.method_var = tk.StringVar(value="extractive")
        method_combo = ttk.Combobox(options_frame, textvariable=self.method_var, 
                                   values=["extractive", "bullet_points", "key_terms"], 
                                   state="readonly", width=15)
        method_combo.grid(row=0, column=1, padx=(5, 20))
        
        # Summary length
        ttk.Label(options_frame, text="Summary Length:").grid(row=0, column=2, sticky=tk.W)
        self.length_var = tk.StringVar(value="medium")
        length_combo = ttk.Combobox(options_frame, textvariable=self.length_var, 
                                   values=["short", "medium", "long"], 
                                   state="readonly", width=10)
        length_combo.grid(row=0, column=3, padx=(5, 20))
        
        # Summarize button
        summarize_btn = ttk.Button(options_frame, text="Summarize Notes", 
                                  command=self.summarize_notes)
        summarize_btn.grid(row=0, column=4, padx=(20, 0))
        
        # Output section
        ttk.Label(main_frame, text="Summary:").grid(row=5, column=0, sticky=tk.W)
        
        # Save button
        save_btn = ttk.Button(main_frame, text="Save Summary", 
                             command=self.save_summary)
        save_btn.grid(row=5, column=2, sticky=tk.E)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(main_frame, height=12, width=70)
        self.output_text.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                             pady=(5, 0))
        
        # Status bar 
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_file(self):
        """Load notes from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Notes File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        ) 
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(1.0, content)
                    self.status_var.set(f"Loaded: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def save_summary(self):
        """Save summary to a text file"""
        content = self.output_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No summary to save!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Summary",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    self.status_var.set(f"Saved: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def calculate_sentence_scores(self, sentences):
        """Calculate importance scores for sentences"""
        # Create word frequency dictionary
        word_freq = Counter()
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            word_freq.update(words)
        
        # Calculate sentence scores
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            words = re.findall(r'\b\w+\b', sentence.lower())
            score = 0
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
            
            # Bonus for sentence position (earlier sentences often more important)
            position_bonus = 1.0 - (i / len(sentences)) * 0.3
            score *= position_bonus
            
            # Bonus for sentence length (moderate length preferred)
            length_bonus = 1.0 if 10 <= len(words) <= 25 else 0.8
            score *= length_bonus
            
            sentence_scores[i] = score
        
        return sentence_scores
    
    def extractive_summary(self, text, target_sentences):
        """Create extractive summary by selecting top sentences"""
        sentences = self.preprocess_text(text)
        if len(sentences) <= target_sentences:
            return text
        
        sentence_scores = self.calculate_sentence_scores(sentences)
        
        # Select top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        selected_indices = sorted([idx for idx, score in top_sentences[:target_sentences]])
        
        # Reconstruct summary maintaining original order
        summary = '. '.join([sentences[i] for i in selected_indices])
        return summary + '.'
    
    def bullet_point_summary(self, text):
        """Create bullet point summary of key concepts"""
        sentences = self.preprocess_text(text)
        sentence_scores = self.calculate_sentence_scores(sentences)
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Create bullet points
        bullet_points = []
        for idx, score in top_sentences[:8]:  # Top 8 points
            sentence = sentences[idx]
            # Simplify sentence for bullet point
            if len(sentence) > 80:
                sentence = sentence[:77] + "..."
            bullet_points.append(f"• {sentence}")
        
        return '\n'.join(bullet_points)
    
    def key_terms_summary(self, text):
        """Extract key terms and concepts"""
        # Find all words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                       'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
                       'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
                       'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 
                       'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 
                       'its', 'our', 'their'}
        
        # Count word frequencies
        word_freq = Counter(word for word in words if word not in common_words and len(word) > 2)
        
        # Get top terms
        top_terms = word_freq.most_common(15)
        # Create summary   kj
        summary = "KEY TERMS AND CONCEPTS:\n\n"
        for term, freq in top_terms:
            summary += f"• {term.capitalize()} (mentioned {freq} times)\n"
        
        # Add context for top terms
        sentences = self.preprocess_text(text)
        summary += "\nKEY CONCEPTS IN CONTEXT:\n\n"
        
        for term, freq in top_terms[:5]:  # Top 5 terms
            for sentence in sentences:
                if term in sentence.lower():
                    summary += f"• {sentence}\n"
                    break
        
        return summary
    
    def summarize_notes(self):
        """Main summarization function"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Warning", "Please enter some notes to summarize!")
            return
        
        self.status_var.set("Summarizing...")
        
        try:
            method = self.method_var.get()
            length = self.length_var.get()
            
            # Determine target length
            sentences = self.preprocess_text(input_text)
            total_sentences = len(sentences)
            
            if length == "short":
                target_sentences = max(2, total_sentences // 4)
            elif length == "medium":
                target_sentences = max(3, total_sentences // 3)
            else:  # long
                target_sentences = max(4, total_sentences // 2)
            
            # Generate summary based on method
            if method == "extractive":
                summary = self.extractive_summary(input_text, target_sentences)
            elif method == "bullet_points":
                summary = self.bullet_point_summary(input_text)
            elif method == "key_terms":
                summary = self.key_terms_summary(input_text)
            
            # Display summary
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(1.0, summary)
            
            self.status_var.set(f"Summary complete - {method} method, {length} length")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to summarize: {str(e)}")
            self.status_var.set("Error occurred")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = NoteSummarizer()
    app.run()

if __name__ == "__main__":
    main()