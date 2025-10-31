#!/usr/bin/env python3
"""
Система управления контактами - MVD версия
Философия: Минимально жизнеспособные данные (3 поля)

ЦЕЛЬ: Разослать приглашение на тур Paris-2026 и помнить, кто откликнулся

MVD (3 поля):
- Имя: для персонализации
- Контакт: Email/Telegram/Phone (любой тип)
- Статус: Не отправлено / Отправлено / Откликнулся / Отказался
"""

import csv
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Contact:
    """Минимально жизнеспособный контакт"""
    name: str
    contact: str  # Email/TG/Phone - что есть
    status: str   # Не отправлено / Отправлено / Откликнулся / Отказался


class ContactManager:
    """Минималистичный менеджер контактов"""
    
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.contacts = []
    
    def load(self):
        """Загрузка контактов"""
        if not self.csv_path.exists():
            return
        
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.contacts.append(Contact(
                    name=row['Имя'],
                    contact=row['Контакт'],
                    status=row['Статус']
                ))
    
    def save(self):
        """Сохранение контактов"""
        with open(self.csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Имя', 'Контакт', 'Статус'])
            writer.writeheader()
            
            # Сортировка по имени
            sorted_contacts = sorted(self.contacts, key=lambda c: c.name)
            
            for c in sorted_contacts:
                writer.writerow({
                    'Имя': c.name,
                    'Контакт': c.contact,
                    'Статус': c.status
                })
    
    def not_sent(self):
        """Контакты, которым еще не отправлено"""
        return [c for c in self.contacts if c.status == 'Не отправлено']
    
    def stats(self):
        """Статистика"""
        total = len(self.contacts)
        by_status = {}
        for c in self.contacts:
            by_status[c.status] = by_status.get(c.status, 0) + 1
        
        print(f"\nВсего контактов: {total}")
        for status, count in by_status.items():
            print(f"  {status}: {count}")


def main():
    """Ежедневное использование"""
    # Контакты находятся в SHARED/contacts/ категории Дизайн-путешествия
    contacts_root = Path(__file__).parent.parent
    csv_path = contacts_root / "ADDRESS_LIST.csv"
    
    manager = ContactManager(csv_path)
    manager.load()
    
    print("=== КОНТАКТЫ ДЛЯ РАССЫЛКИ ===\n")
    
    not_sent = manager.not_sent()
    if not_sent:
        print(f"Не отправлено приглашений: {len(not_sent)}\n")
        for c in not_sent[:10]:  # Показываем первые 10
            print(f"• {c.name} ({c.contact})")
        if len(not_sent) > 10:
            print(f"\n... и еще {len(not_sent) - 10}")
    else:
        print("Все приглашения отправлены.")
    
    manager.stats()


if __name__ == "__main__":
    main()

