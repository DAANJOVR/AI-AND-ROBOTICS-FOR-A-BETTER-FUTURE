import customtkinter as ctk
import json
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
import random
import requests
import threading

# --------------------------------------
# STORAGE FILES
# --------------------------------------
FLASHCARD_FILE = "flashcards.json"

# --------------------------------------
# JSON UTILITIES
# --------------------------------------
def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --------------------------------------
# FLASHCARD UTILITIES
# --------------------------------------
def load_flashcards():
    """Always return list of flashcards without crashing."""
    if not os.path.exists(FLASHCARD_FILE):
        return []

    try:
        with open(FLASHCARD_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                for card in data:
                    if "question" not in card:
                        card["question"] = ""
                    if "answer" not in card:
                        card["answer"] = ""
                    if "correct" not in card:
                        card["correct"] = 0
                    if "wrong" not in card:
                        card["wrong"] = 0
                return data
            return []
    except:
        return []

def save_flashcards(data):
    with open(FLASHCARD_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --------------------------------------
# OLLAMA AI QUERY
# --------------------------------------
def query_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen:0.5b", "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "")
        return None
    except:
        return None

# --------------------------------------
# NOTES + QUESTION GENERATION
# --------------------------------------
def generate_notes(topic):
    prompt = (
        f"Generate structured study notes on the topic '{topic}'. "
        f"Include intro, key concepts, examples, summary."
    )
    ai = query_ollama(prompt)
    if ai:
        return f"📘 NOTES ON {topic}\n\n{ai}"

    return (
        f"📘 NOTES ON {topic}\n"
        "- Introduction\n- Key Concepts\n- Examples\n- Summary (Fallback)"
    )

def generate_questions(subject):
    prompt = (
        f"Generate 5 exam questions for '{subject}'. Including MCQ, short answer, "
        "application, problem solving, bonus."
    )
    ai = query_ollama(prompt)
    if ai:
        return f"📝 QUESTIONS ON {subject}\n\n{ai}"

    return (
        "📝 QUESTIONS (Fallback)\n"
        "1. MCQ\n2. Short Answer\n3. Application\n4. Problem\n5. Bonus"
    )

# --------------------------------------
# PDF EXPORT
# --------------------------------------
def export_pdf(filename, title, content):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=40, leftMargin=40)
    elements = [Paragraph(title, styles["Title"]), Spacer(1, 0.3 * inch)]

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["BodyText"]))
        elements.append(Spacer(1, 0.08 * inch))

    doc.build(elements)

# --------------------------------------
# PURE AI TUTOR LOGIC (NO FLASHCARD MODE)
# --------------------------------------
def generate_ai_response(user_question, flashcards):
    """
    PURE AI MODE:
    - Flashcards NEVER interfere.
    - Flashcards NEVER override the answer.
    - Flashcards are NOT searched.
    - No fallback.
    """

    prompt = (
        "You are EduMind AI Tutor. Provide a clear, detailed explanation. "
        "Ignore flashcards completely. Always answer using your own reasoning.\n\n"
        f"User Question: {user_question}"
    )

    ai = query_ollama(prompt)
    if ai:
        return ai.strip()

    # If AI fails (Ollama down)
    return "AI engine is unavailable right now. Please try again."

# ====================================================================
#                           MAIN GUI CLASS
# ====================================================================
class StudyTutorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("🧠 EduMind AI Pro")
        self.geometry("1000x700")
        self.resizable(False, False)

        # Tabs
        self.tabs = ctk.CTkTabview(self, width=970, height=650)
        self.tabs.pack(padx=15, pady=15)

        for t in ["Notes", "Questions", "Flashcards", "AI Tutor", "Quizzes", "Export"]:
            self.tabs.add(t)

        self.build_notes_tab()
        self.build_questions_tab()
        self.build_flashcards_tab()
        self.build_ai_tutor_tab()
        self.build_quiz_tab()
        self.build_export_tab()

    # ------------------------------ NOTES TAB ------------------------------
    def build_notes_tab(self):
        tab = self.tabs.tab("Notes")

        self.topic_entry_notes = ctk.CTkEntry(tab, placeholder_text="Enter topic")
        self.topic_entry_notes.pack(pady=10)

        ctk.CTkButton(tab, text="Generate Notes", command=self.generate_notes_gui).pack()

        self.notes_text = ctk.CTkTextbox(tab)
        self.notes_text.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkButton(tab, text="Export to PDF", command=self.export_notes_pdf).pack(pady=10)

    def generate_notes_gui(self):
        topic = self.topic_entry_notes.get()
        if not topic:
            return

        self.notes_text.delete("0.0", "end")
        self.notes_text.insert("end", "Generating with AI...\n")
        self.update()

        def worker():
            content = generate_notes(topic)
            self.notes_text.delete("0.0", "end")
            self.notes_text.insert("0.0", content)

        threading.Thread(target=worker).start()

    def export_notes_pdf(self):
        topic = self.topic_entry_notes.get()
        content = self.notes_text.get("0.0", "end")
        export_pdf(f"{topic}_notes.pdf", f"Notes on {topic}", content)

    # ------------------------------ QUESTIONS TAB ------------------------------
    def build_questions_tab(self):
        tab = self.tabs.tab("Questions")

        self.subject_entry = ctk.CTkEntry(tab, placeholder_text="Enter subject")
        self.subject_entry.pack(pady=10)

        ctk.CTkButton(tab, text="Generate Questions", command=self.generate_questions_gui).pack()

        self.questions_text = ctk.CTkTextbox(tab)
        self.questions_text.pack(expand=True, fill="both", padx=10, pady=10)

        ctk.CTkButton(tab, text="Export to PDF", command=self.export_questions_pdf).pack(pady=10)

    def generate_questions_gui(self):
        subject = self.subject_entry.get()
        if not subject:
            return

        self.questions_text.delete("0.0", "end")
        self.questions_text.insert("end", "Generating with AI...\n")
        self.update()

        def worker():
            content = generate_questions(subject)
            self.questions_text.delete("0.0", "end")
            self.questions_text.insert("0.0", content)

        threading.Thread(target=worker).start()

    def export_questions_pdf(self):
        subject = self.subject_entry.get()
        content = self.questions_text.get("0.0", "end")
        export_pdf(f"{subject}_questions.pdf", f"Questions on {subject}", content)

    # ------------------------------ FLASHCARDS TAB ------------------------------
    def delete_all_flashcards(self):
        save_flashcards([])
        self.flashcards_text.delete("0.0", "end")
        self.flashcards_text.insert("0.0", "All flashcards deleted!\n")

    def build_flashcards_tab(self):
        tab = self.tabs.tab("Flashcards")

        self.q_entry = ctk.CTkEntry(tab, placeholder_text="Question")
        self.q_entry.pack(pady=5)

        self.a_entry = ctk.CTkEntry(tab, placeholder_text="Answer")
        self.a_entry.pack(pady=5)

        ctk.CTkButton(tab, text="Add Flashcard", command=self.add_flashcard_gui).pack(pady=10)
        ctk.CTkButton(tab, text="Review Flashcards", command=self.review_flashcards_gui).pack(pady=5)
        ctk.CTkButton(tab, text="Take Quiz", command=self.quiz_mode_gui).pack(pady=5)
        ctk.CTkButton(tab, text="Show Stats", command=self.show_stats_gui).pack(pady=5)
        ctk.CTkButton(
            tab, text="Delete All Flashcards",
            fg_color="red", hover_color="#8b0000",
            command=self.delete_all_flashcards
        ).pack(pady=10)

        self.flashcards_text = ctk.CTkTextbox(tab)
        self.flashcards_text.pack(expand=True, fill="both", padx=10, pady=10)

    def add_flashcard_gui(self):
        q = self.q_entry.get()
        a = self.a_entry.get()
        if not q or not a:
            return

        flashcards = load_flashcards()
        flashcards.append({
            "question": q,
            "answer": a,
            "correct": 0,
            "wrong": 0
        })
        save_flashcards(flashcards)

        self.flashcards_text.insert("end", f"Added: {q} -> {a}\n")
        self.q_entry.delete(0, "end")
        self.a_entry.delete(0, "end")

    def review_flashcards_gui(self):
        flashcards = load_flashcards()
        if not flashcards:
            return
        ReviewWindow(flashcards)

    def quiz_mode_gui(self):
        flashcards = load_flashcards()
        if not flashcards:
            return
        QuizWindow(flashcards)

    def show_stats_gui(self):
        flashcards = load_flashcards()
        win = ctk.CTkToplevel(self)
        win.title("Flashcard Stats")
        win.geometry("600x400")

        text = ctk.CTkTextbox(win)
        text.pack(expand=True, fill="both", padx=10, pady=10)

        for card in flashcards:
            text.insert(
                "end",
                f"Q: {card['question']}\nCorrect: {card['correct']}  |  Wrong: {card['wrong']}\n\n"
            )

    # ------------------------------ AI TUTOR TAB ------------------------------
    def build_ai_tutor_tab(self):
        tab = self.tabs.tab("AI Tutor")

        self.chat_history = ctk.CTkTextbox(tab)
        self.chat_history.pack(expand=True, fill="both", padx=10, pady=10)
        self.chat_history.insert("0.0", "AI Tutor: Hello! Ask me anything.\n\n")
        self.chat_history.configure(state="disabled")

        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=10, pady=10)

        self.chat_entry = ctk.CTkEntry(frame, placeholder_text="Ask something...")
        self.chat_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkButton(frame, text="Send", command=self.send_message).pack(side="right")

    def send_message(self):
        user_msg = self.chat_entry.get().strip()
        if not user_msg:
            return

        self.chat_entry.delete(0, "end")

        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"You: {user_msg}\n\n")
        self.chat_history.insert("end", "AI Tutor: Thinking...\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

        def worker():
            flashcards = load_flashcards()
            response = generate_ai_response(user_msg, flashcards)

            self.chat_history.configure(state="normal")
            self.chat_history.delete("end-2l", "end")
            self.chat_history.insert("end", f"AI Tutor: {response}\n\n")
            self.chat_history.configure(state="disabled")
            self.chat_history.see("end")

        threading.Thread(target=worker).start()

    # ------------------------------ QUIZ TAB ------------------------------
    def build_quiz_tab(self):
        tab = self.tabs.tab("Quizzes")
        ctk.CTkButton(tab, text="Start Quiz", command=self.quiz_mode_gui).pack(pady=10)
        self.quiz_text = ctk.CTkTextbox(tab)
        self.quiz_text.pack(expand=True, fill="both", padx=10, pady=10)

    # ------------------------------ EXPORT TAB ------------------------------
    def build_export_tab(self):
        tab = self.tabs.tab("Export")
        ctk.CTkLabel(tab, text="Use Export buttons in Notes/Questions tabs.").pack(expand=True)

# ====================================================================
#                         REVIEW WINDOW
# ====================================================================
class ReviewWindow(ctk.CTkToplevel):
    def __init__(self, flashcards):
        super().__init__()
        self.title("Review Flashcards")
        self.geometry("600x400")

        self.flashcards = flashcards
        self.index = 0

        self.show_question()

    def show_question(self):
        self.clear()
        if self.index >= len(self.flashcards):
            ctk.CTkLabel(self, text="Review Complete!").pack(pady=20)
            return

        card = self.flashcards[self.index]

        ctk.CTkLabel(self, text=f"Q: {card['question']}", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self, text="Reveal Answer", command=self.show_answer).pack(pady=10)

    def show_answer(self):
        card = self.flashcards[self.index]
        ctk.CTkLabel(self, text=f"A: {card['answer']}", font=("Arial", 14)).pack(pady=10)
        ctk.CTkButton(self, text="Next", command=self.next_card).pack(pady=10)

    def next_card(self):
        self.index += 1
        self.show_question()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

# ====================================================================
#                         QUIZ WINDOW
# ====================================================================
class QuizWindow(ctk.CTkToplevel):
    def __init__(self, flashcards):
        super().__init__()
        self.title("Quiz Mode")
        self.geometry("600x400")

        self.flashcards = flashcards.copy()
        random.shuffle(self.flashcards)

        self.index = 0
        self.score = 0

        self.show_question()

    def show_question(self):
        self.clear()

        if self.index >= len(self.flashcards):
            return self.show_results()

        card = self.flashcards[self.index]
        ctk.CTkLabel(self, text=f"Question: {card['question']}", font=("Arial", 16)).pack(pady=20)

        self.entry = ctk.CTkEntry(self, placeholder_text="Your answer")
        self.entry.pack(pady=10)

        ctk.CTkButton(self, text="Submit", command=self.check_answer).pack(pady=10)

    def check_answer(self):
        user = self.entry.get().strip().lower()
        card = self.flashcards[self.index]
        correct = card["answer"].strip().lower()

        if user == correct:
            card["correct"] += 1
            msg = "✔ Correct!"
            self.score += 1
        else:
            card["wrong"] += 1
            msg = f"✘ Wrong! Correct: {card['answer']}"

        save_flashcards(self.flashcards)

        ctk.CTkLabel(self, text=msg).pack(pady=10)
        ctk.CTkButton(self, text="Next", command=self.next_question).pack(pady=10)

    def next_question(self):
        self.index += 1
        self.show_question()

    def show_results(self):
        self.clear()
        ctk.CTkLabel(
            self,
            text=f"Score: {self.score}/{len(self.flashcards)}",
            font=("Arial", 16)
        ).pack(pady=20)
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

# ====================================================================
#                           RUN APP
# ====================================================================
if __name__ == "__main__":
    app = StudyTutorApp()
    app.mainloop()
