from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    text: str
    page_number: int | None = Field(default=None, ge=1)
    source_text: str | None = None


class Experience(SourceItem):
    role: str | None = None
    company: str | None = None
    duration: str | None = None


class Project(SourceItem):
    name: str | None = None
    description: str | None = None


class Education(SourceItem):
    degree: str | None = None
    institution: str | None = None
    graduation_year: str | None = None


class Certification(SourceItem):
    name: str | None = None
    issuer: str | None = None


class ResumeProfile(BaseModel):
    text: str = ""
    skills: list[str] = []
    programming_languages: list[str] = []
    frameworks: list[str] = []
    libraries: list[str] = []
    tools: list[str] = []
    databases: list[str] = []
    cloud: list[str] = []
    experience: list[Experience] = []
    projects: list[Project] = []
    education: list[Education] = []
    certifications: list[Certification] = []


class JobDescription(BaseModel):
    text: str = ""
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    programming_languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []
    databases: list[str] = []
    cloud: list[str] = []
    experience_requirements: list[str] = []
    education_requirements: list[str] = []
    responsibilities: list[str] = []


class ExtractionResponse(BaseModel):
    filename: str
    extraction: ResumeProfile | JobDescription
