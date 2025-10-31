#!/usr/bin/env python3
"""
Синхронизация тегированных контактов обратно в ADDRESS_LIST.csv
Принцип q1: Автоматизация ручной работы

После тегирования в tagging_ui.html:
1. Ольга нажимает "Экспортировать CSV"
2. Скачивается ADDRESS_LIST_TAGGED.csv в Downloads
3. Запускается этот скрипт: python3 tools/sync_tagged_contacts.py
4. Теги и заметки автоматически применяются к ADDRESS_LIST.csv
"""

import csv
import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class TaggedContactsSyncer:
    """Синхронизатор тегированных контактов"""

    def __init__(self, address_list_path: str = "../ADDRESS_LIST.csv"):
        self.address_list_path = Path(__file__).parent.parent / "ADDRESS_LIST.csv"
        self.contacts: Dict[str, dict] = {}
        self.load_address_list()

    def load_address_list(self):
        """Загрузка текущего ADDRESS_LIST.csv"""
        if not self.address_list_path.exists():
            print(f"ADDRESS_LIST.csv не найден: {self.address_list_path}")
            return

        with open(self.address_list_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Используем email или phone как ключ
                key = row.get('Email', '').strip() or row.get('Phone', '').strip()
                if key:
                    self.contacts[key] = row

        print(f"Загружено {len(self.contacts)} контактов из ADDRESS_LIST.csv")

    def find_tagged_csv(self) -> Path:
        """Поиск скачанного CSV файла с тегированными контактами"""
        # Возможные пути
        possible_paths = [
            Path.home() / "Downloads" / "ADDRESS_LIST_TAGGED.csv",
            Path.home() / "Desktop" / "ADDRESS_LIST_TAGGED.csv",
            Path(__file__).parent.parent / "ADDRESS_LIST_TAGGED.csv",
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Поиск по паттерну в Downloads
        downloads = Path.home() / "Downloads"
        if downloads.exists():
            for file in downloads.glob("*TAGGED*.csv"):
                return file

        return None

    def sync_tagged_contacts(self, tagged_csv_path: Path):
        """Синхронизация тегированных контактов"""
        if not tagged_csv_path.exists():
            print(f"Файл не найден: {tagged_csv_path}")
            return 0

        updated = 0
        with open(tagged_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Используем email или phone как ключ
                key = row.get('Email', '').strip() or row.get('Phone', '').strip()
                if not key:
                    continue

                # Ищем контакт в основном списке
                if key in self.contacts:
                    contact = self.contacts[key]

                    # Обновляем тег и заметки
                    old_tag = contact.get('Tag', '')
                    old_notes = contact.get('Notes', '')
                    new_tag = row.get('Tag', '').strip()
                    new_notes = row.get('Notes', '').strip()

                    changed = False
                    if new_tag != old_tag:
                        contact['Tag'] = new_tag
                        changed = True
                        print(f"Обновлен тег для {key}: '{old_tag}' → '{new_tag}'")

                    if new_notes != old_notes:
                        contact['Notes'] = new_notes
                        changed = True
                        print(f"Обновлены заметки для {key}: '{old_notes}' → '{new_notes}'")

                    if changed:
                        updated += 1
                else:
                    print(f"Предупреждение: контакт {key} не найден в ADDRESS_LIST.csv")

        return updated

    def save_address_list(self):
        """Сохранение обновленного ADDRESS_LIST.csv"""
        with open(self.address_list_path, 'w', encoding='utf-8', newline='') as f:
            if self.contacts:
                fieldnames = list(self.contacts.values())[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                # Сортировка по дате добавления (новые первыми)
                sorted_contacts = sorted(
                    self.contacts.values(),
                    key=lambda c: c.get('DateAdded', '') or '',
                    reverse=True
                )

                writer.writerows(sorted_contacts)

        print(f"Сохранено {len(self.contacts)} контактов в ADDRESS_LIST.csv")


def main():
    """Основная функция"""
    print("=== СИНХРОНИЗАЦИЯ ТЕГИРОВАННЫХ КОНТАКТОВ ===\n")

    syncer = TaggedContactsSyncer()

    # Поиск файла с тегированными контактами
    tagged_csv = syncer.find_tagged_csv()
    if not tagged_csv:
        print("❌ Файл ADDRESS_LIST_TAGGED.csv не найден!")
        print("\nВозможные пути:")
        print("- ~/Downloads/ADDRESS_LIST_TAGGED.csv")
        print("- ~/Desktop/ADDRESS_LIST_TAGGED.csv")
        print("- ADDRESS_LIST_TAGGED.csv (в корне проекта)")
        print("\nУбедитесь, что вы экспортировали CSV из tagging_ui.html")
        return

    print(f"Найден файл: {tagged_csv}")

    # Синхронизация
    updated = syncer.sync_tagged_contacts(tagged_csv)

    if updated > 0:
        # Сохранение изменений
        syncer.save_address_list()

        # Удаление скачанного файла (опционально)
        try:
            tagged_csv.unlink()
            print(f"Удален временный файл: {tagged_csv}")
        except:
            pass

        print(f"\n✅ Синхронизировано {updated} контактов!")
        print("ADDRESS_LIST.csv обновлен.")
    else:
        print("\nℹ️  Изменений не найдено.")

    print("\n✓ Готово!")


if __name__ == "__main__":
    main()



