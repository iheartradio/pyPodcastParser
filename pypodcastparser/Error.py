
class TagError(Exception):
    def __init__(self, tag_name="tag_name", tag_content="tag_content"):
        self.tag_name = tag_name
        self.tag_content = tag_content
        super().__init__(f"Error parsing xml item tag {tag_name} with contents: {tag_content}")