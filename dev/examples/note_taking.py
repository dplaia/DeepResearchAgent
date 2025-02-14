class ReferenceManager():
    def __init__(self, save_directory: str):
        self.refs: dict[str, str] = {}
        self.save_directory: str = save_directory
        os.makedirs(save_directory, exist_ok=True)

    def add_reference(self, link: str, markdown_text: str, filename: str) -> None:
        """Adds a reference with validation of inputs and error handling."""
        if not link.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid link format: {link}")

        if not filename.endswith('.md'):
            filename += '.md'

        if not self.check_ref(link):
            try:
                self.save_markdown(filename, markdown_text)
                self.refs[link] = filename
            except IOError as e:
                print(f"Failed to save {filename}: {str(e)}")

    def check_ref(self, link: str) -> bool:
        return link in self.refs

    def get_markdown_text(self, link: str) -> Optional[str]:

        if filename := self.refs.get(link):
            try:
                return self.read_markdown_file(filename)
            except FileNotFoundError:
                return None
        return None

    def save_markdown(self, filename: str, markdown_text: str) -> None:
        full_path = join(self.save_directory, filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(markdown_text)

    def read_markdown_file(self, filename: str) -> str:
        full_path = join(self.save_directory, filename)
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise

@dataclass
class DocumentInfo:
    id: UUID
    title: str
    note_count: int
    created_at: Optional[datetime]
    last_updated: Optional[datetime]

class NoteManager:
    def __init__(self):
        self.documents: Dict[UUID, DocumentNotes] = {}
        self.document_titles: Dict[str, UUID] = {}  # Prevent duplicate titles

    def create_document(self, title: str) -> UUID:
        """Creates a new document with unique title validation"""
        if title in self.document_titles:
            raise ValueError(f"Document title '{title}' already exists")
            
        doc_id = uuid4()
        self.documents[doc_id] = DocumentNotes(title)
        self.document_titles[title] = doc_id
        return doc_id

    def get_all_documents(self) -> List[DocumentInfo]:
        """Returns metadata about all documents with temporal statistics"""
        return [
            DocumentInfo(
                id=doc_id,
                title=doc.title,
                note_count=len(doc.notes),
                created_at=min(note.created_at for note in doc.notes.values()) if doc.notes else None,
                last_updated=max(note.updated_at for note in doc.notes.values()) if doc.notes else None
            )
            for doc_id, doc in self.documents.items()
        ]

@dataclass
class Note:
    id: UUID # Unique identifier using UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

@dataclass
class DocumentNotes:
    title: str
    notes: Dict[UUID, Note] = field(default_factory=dict)
    
    def add_note(self, title: str, content: str) -> UUID:
        """Adds a new note with creation timestamp"""
        note_id = uuid4()
        now = datetime.now()
        self.notes[note_id] = Note(
            id=note_id,
            title=title,
            content=content,
            created_at=now,
            updated_at=now
        )
        return note_id

    def update_note(self, note_id: UUID, new_content: str) -> None:
        """Updates existing note with conflict checking"""
        if note_id not in self.notes:
            raise KeyError(f"Note {note_id} not found")
            
        self.notes[note_id].content += f"\n\n--- Update {datetime.now()} ---\n{new_content}"
        self.notes[note_id].updated_at = datetime.now()

    def get_note(self, note_id: UUID) -> Optional[Note]:
        """Safer retrieval with explicit None return"""
        return self.notes.get(note_id)

    def get_all_notes(self) -> Dict[UUID, Note]:
        """Returns direct reference to notes dict"""
        return self.notes.copy()  # Return copy to prevent accidental mutation


# Initialize the note management system
manager = NoteManager()

# Create two documents
research_id = manager.create_document("Research Paper")
meeting_id = manager.create_document("Meeting Minutes")

# Add notes to first document
methodology_note_id = manager.documents[research_id].add_note(
    "Methodology",
    "Need to revise sampling methodology section"
)

methodology_note_id = manager.documents[research_id].add_note(
    "Shows creation time",
    "Creation time should be shown."
)

# Add notes to second document
action_items_id = manager.documents[meeting_id].add_note(
    "Action Items",
    "1. Schedule follow-up meeting\n2. Prepare Q2 budget"
)

# Update a note in the first document
manager.documents[research_id].update_note(
    methodology_note_id,
    "Added new randomization procedure details"
)

# Retrieve and print a specific note
def print_note(doc_id: UUID, note_id: UUID):
    doc = manager.documents[doc_id]
    note = doc.get_note(note_id)
    if note:
        print(f"\n--- Note: {note.title} ---")
        print(f"Created: {note.created_at}")
        print(f"Last Updated: {note.updated_at}")
        print(f"Content:\n{note.content}\n")
    else:
        print("Note not found")

# Print updated methodology note
print_note(research_id, methodology_note_id)

# Example of failed update (non-existent note)
try:
    manager.documents[meeting_id].update_note(
        UUID('00000000-0000-0000-0000-000000000000'),
        "This shouldn't work"
    )
except KeyError as e:
    print(f"\nError: {str(e)}")

# Retrieve all notes from meeting document
print("\nAll meeting notes:")
for note_id, note in manager.documents[meeting_id].get_all_notes().items():
    print(f" - {note.title}: {note.content[:50]}...")


id = manager.get_all_documents()[0].id

notes = manager.documents[id].get_all_notes()
for note_id in notes:
    print(notes[note_id].title)
    print(notes[note_id].content)
    print()

page_content_markdown = {}
for link in result.data.links:
    print(f"Link: {link}")
    markdown = await crawl4ai_website_async(link)
    page_content_markdown[link] = markdown

system_prompt = """
You are an expert at writing professional technical writer (articles, blogs, books, etc.).

After receiving a user query and some files, your goal is to write an report about the user query.
This writen report should be technically detailed but comprehensive for normal readers.

Please use references in the report (e.g. [1]). You can find the link of a given input text above the text with "From link ([1] http ...)".

Always use References at the end of the report.
  
Write the output strictly in Markdown format. 
"""

summary_agent = Agent(
    model,
    result_type=str,
    system_prompt=system_prompt)


result = await summary_agent.run(combined_markdown)

console.print(Markdown(result.data))