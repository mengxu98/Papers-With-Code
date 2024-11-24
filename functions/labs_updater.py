from .base_updater import BaseUpdater
import yaml

class LabsUpdater(BaseUpdater):
    def __init__(self):
        """Initialize labs updater"""
        super().__init__('config/labs.yaml')
        self.md_file = 'website/content/posts/labs.md'
        
    def update_content(self, data=None):
        """
        Update content in both yaml and md files
        Args:
            data: Optional data to update yaml with
        Returns:
            bool: Success status
        """
        try:
            self.logger.info("Starting labs update")
            
            # First ensure yaml file is up to date
            if data is None:
                yaml_data = self._load_yaml()
                if yaml_data is None:
                    return False
            else:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
                yaml_data = data
            
            self.logger.info(f"Loaded {len(yaml_data)} entries from YAML")

            # Validate entries
            valid_entries = []
            for entry in yaml_data:
                if not isinstance(entry, dict):
                    self.logger.warning(f"Skipping invalid entry: {entry}")
                    continue
                    
                # Use title as name if name is not provided
                if 'name' not in entry and 'title' in entry:
                    entry['name'] = entry['title']
                    
                # Check required fields
                if 'name' not in entry or 'url' not in entry:
                    self.logger.warning(f"Skipping entry without name or url: {entry}")
                    continue
                    
                valid_entries.append(entry)
            
            self.logger.info(f"Found {len(valid_entries)} valid entries")

            # Create or update MD file
            try:
                with open(self.md_file, 'r', encoding='utf-8') as f:
                    content = f.readlines()
                self.logger.info(f"Reading existing MD file: {self.md_file}")
            except FileNotFoundError:
                content = [
                    '---\n',
                    'title: "Labs"\n',
                    'date: 2024-01-01\n',
                    'draft: false\n',
                    '---\n',
                    '\n',
                    'This page lists research labs and groups working on bioinformatics and computational biology.\n',
                    '\n'
                ]
                self.logger.info(f"Creating new MD file: {self.md_file}")

            # Find or create table section
            table_start = None
            for i, line in enumerate(content):
                if line.startswith('| **Name**'):
                    table_start = i
                    self.logger.debug(f"Found table start at line {i}")
                    break

            # Create new table content
            self.logger.info("Creating new table content")
            new_table = ['| **Name** | **PI** | **Institution** | **Research** |\n',
                        '| -- | -- | -- | -- |\n']
            
            # Group entries by category
            entries_by_category = {}
            for entry in valid_entries:
                category = entry.get('category', 'Other')
                if category not in entries_by_category:
                    entries_by_category[category] = []
                entries_by_category[category].append(entry)
            
            self.logger.info(f"Found {len(entries_by_category)} categories")

            # Add entries by category
            for category in sorted(entries_by_category.keys()):
                self.logger.debug(f"Processing category: {category}")
                new_table.append(f'| **`{category}`** |  |  |  |\n')
                for entry in sorted(entries_by_category[category], key=lambda x: x['name']):
                    self.logger.debug(f"Processing entry: {entry['name']}")
                    
                    # Create name with link
                    name_cell = f"[{entry['name']}]({entry['url']})"

                    line = f"| {name_cell} | {entry.get('pi', '')} | {entry.get('institution', '')} | {entry.get('research', '')} |\n"
                    new_table.append(line)

            # Replace or append table
            if table_start is not None:
                # Find table end
                table_end = table_start
                while table_end < len(content) and content[table_end].startswith('|'):
                    table_end += 1
                
                self.logger.info(f"Replacing table content from line {table_start} to {table_end}")
                content[table_start:table_end] = new_table
            else:
                # Append table to end of file
                self.logger.info("Appending new table to end of file")
                if content and not content[-1].endswith('\n'):
                    content.append('\n')
                content.extend(new_table)

            # Write back to file
            self.logger.info(f"Writing updated content to {self.md_file}")
            with open(self.md_file, 'w', encoding='utf-8') as f:
                f.writelines(content)

            self.logger.info(f"Successfully updated {self.md_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error updating content: {str(e)}")
            self.logger.exception("Full traceback:")
            return False 