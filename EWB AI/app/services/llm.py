"""All local-LLM logic lives here (Ollama + LangChain)."""
from fastapi import HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from .grading import grade_for, risk_for

llm = ChatOllama(model="llama3.2", temperature=0.2)

# 1) Free-form Q&A over the whole database
ask_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are EduMentor, an academic assistant for a training institute. "
     "Answer ONLY from the student records below. If the answer is not "
     "there, say you don't know. Be short and clear.\n\n"
     "STUDENT RECORDS:\n{records}"),
    ("human", "{question}"),
])

# 2) Personal mentor report for ONE student
report_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly, encouraging mentor. Write a short mentor report "
     "with exactly these headings: Summary, Strengths, Areas to Improve, "
     "7-Day Action Plan. Use simple English and keep it under 180 words."),
    ("human",
     "Student: {name}\nCourse: {course}\nMarks: {marks}/100 (Grade {grade})\n"
     "Attendance: {attendance}%\nRisk level: {risk}\nSkills: {skills}\n"
     "Class average marks: {class_avg}"),
])


def student_line(s) -> str:
    return (f"ID={s.id} | {s.name} | {s.course} | marks={s.marks} "
            f"(grade {grade_for(s.marks)}) | attendance={s.attendance}% | "
            f"risk={risk_for(s.marks, s.attendance)} | skills={s.skills or '-'}")


def _run(chain, data: dict) -> str:
    try:
        return chain.invoke(data).content
    except Exception as e:
        raise HTTPException(
            503,
            "Local AI is not reachable. Run `ollama serve` and "
            f"`ollama pull llama3.2`. Details: {e}",
        )


def ask(students, question: str) -> str:
    records = "\n".join(student_line(s) for s in students) or "No records."
    return _run(ask_prompt | llm, {"records": records, "question": question})


def mentor_report(student, class_avg: float) -> str:
    return _run(report_prompt | llm, {
        "name": student.name, "course": student.course,
        "marks": student.marks, "grade": grade_for(student.marks),
        "attendance": student.attendance,
        "risk": risk_for(student.marks, student.attendance),
        "skills": student.skills or "not listed",
        "class_avg": round(class_avg, 1),
    })
