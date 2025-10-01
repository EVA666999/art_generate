"""
Тест с 10 вопросами для проверки валидации ответов.
"""
import asyncio
import aiohttp
import json
from typing import List, Dict, Any


class QuestionTester:
    """Класс для тестирования API с различными вопросами."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000/chat"
        self.test_questions = [
            "Hello Anna, how are you?",
            "continue the story", 
            "Say hello in one word",
            "Tell me about yourself",
            "What's your favorite color?",
            "Tell me a very long story about a dragon that goes on and on",
            "Describe your day",
            "What do you think about your brother?",
            "Tell me a joke",
            "What's the weather like today?"
        ]
    
    async def test_single_question(self, session: aiohttp.ClientSession, question: str, question_num: int) -> Dict[str, Any]:
        """Тестирует один вопрос."""
        payload = {
            'message': question,
            'history': [],
            'session_id': f'test_question_{question_num}'
        }
        
        try:
            async with session.post(self.base_url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result['response']
                    
                    # Проверяем завершенность ответа
                    ends_with_punctuation = response_text.strip().endswith(('.', '!', '?', '...', '—', '–', '*'))
                    
                    return {
                         'question': question,
                         'question_num': question_num,
                         'status': 'SUCCESS',
                         'response_length': len(response_text),
                         'ends_with_punctuation': ends_with_punctuation,
                         'full_response': response_text,
                         'last_50_chars': response_text[-50:] if len(response_text) > 50 else response_text
                     }
                elif response.status == 500:
                    error_text = await response.text()
                    return {
                        'question': question,
                        'question_num': question_num,
                        'status': 'REJECTED',
                        'error': error_text,
                        'response_length': 0,
                        'ends_with_punctuation': False
                    }
                else:
                    return {
                        'question': question,
                        'question_num': question_num,
                        'status': 'HTTP_ERROR',
                        'error': f"HTTP {response.status}",
                        'response_length': 0,
                        'ends_with_punctuation': False
                    }
        except Exception as e:
            return {
                'question': question,
                'question_num': question_num,
                'status': 'EXCEPTION',
                'error': str(e),
                'response_length': 0,
                'ends_with_punctuation': False
            }
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Запускает все тесты."""
        results = []
        
        async with aiohttp.ClientSession() as session:
            print("🧪 Запуск тестов с 10 вопросами...")
            print("=" * 60)
            
            for i, question in enumerate(self.test_questions, 1):
                print(f"Тест {i}/10: {question}")
                result = await self.test_single_question(session, question, i)
                results.append(result)
                
                # Выводим результат
                if result['status'] == 'SUCCESS':
                    if result['ends_with_punctuation']:
                        print(f"✅ УСПЕХ: Ответ принят ({result['response_length']} символов)")
                        print(f"   ПОЛНЫЙ ОТВЕТ:")
                        print(f"   \"{result['full_response']}\"")
                    else:
                        print(f"❌ ОШИБКА: Ответ принят, но не заканчивается пунктуацией!")
                        print(f"   ПОЛНЫЙ ОТВЕТ:")
                        print(f"   \"{result['full_response']}\"")
                elif result['status'] == 'REJECTED':
                    print(f"✅ ОТКЛОНЕН: {result['error']}")
                else:
                    print(f"❌ ОШИБКА: {result['status']} - {result['error']}") 
                
                print("-" * 60)
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Выводит сводку результатов."""
        print("\n" + "=" * 60)
        print("📊 СВОДКА РЕЗУЛЬТАТОВ")
        print("=" * 60)
        
        total = len(results)
        success = len([r for r in results if r['status'] == 'SUCCESS' and r['ends_with_punctuation']])
        rejected = len([r for r in results if r['status'] == 'REJECTED'])
        errors = len([r for r in results if r['status'] not in ['SUCCESS', 'REJECTED']])
        success_but_incomplete = len([r for r in results if r['status'] == 'SUCCESS' and not r['ends_with_punctuation']])
        
        print(f"Всего тестов: {total}")
        print(f"✅ Успешно принято: {success}")
        print(f"🚫 Правильно отклонено: {rejected}")
        print(f"❌ Ошибки валидации: {success_but_incomplete}")
        print(f"💥 Системные ошибки: {errors}")
        print()
        
        success_rate = (success + rejected) / total * 100
        print(f"📈 Общий успех: {success_rate:.1f}%")
        
        if success_but_incomplete > 0:
            print(f"⚠️  ПРОБЛЕМА: {success_but_incomplete} ответов приняты, но не завершены!")
            print("   Валидация работает неправильно!")
        else:
            print("✅ Валидация работает правильно!")


async def main():
    """Основная функция тестирования."""
    tester = QuestionTester()
    results = await tester.run_all_tests()
    tester.print_summary(results)


if __name__ == "__main__":
    asyncio.run(main())
