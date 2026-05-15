"""
Quick functional test for BZUF IELTS Bot agents.
Run: python test_bot.py
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from bot.services.groq_service import GroqService
from bot.services.mongodb_service import MongoDBService
from bot.agents.writing_agent import WritingAgent
from bot.agents.speaking_agent import SpeakingAgent
from bot.utils.validators import validate_writing_text, detect_writing_task_type, count_words
from bot.utils.formatters import format_writing_feedback, format_speaking_feedback
from bot.config import settings

# ─── Sample texts ────────────────────────────────────────────────
TASK1_ESSAY = """
The bar chart illustrates the percentage of households in four European countries
that owned at least one car between 1990 and 2010. Overall, car ownership increased
in all four countries over the period, with Luxembourg consistently having the highest
proportion of car-owning households.

In 1990, Luxembourg led with approximately 65% of households owning a car, followed
by France at 55%, Germany at 50%, and the UK at 45%. By 2010, Luxembourg had risen
to 80%, while France and Germany both reached around 70%. The UK showed the most
significant increase, rising from 45% to 68% over the twenty-year period.

It is notable that the gap between Luxembourg and the other three countries narrowed
considerably during this time, suggesting a convergence in car ownership across Europe.
"""

TASK2_ESSAY = """
In today's society, many people argue that television has a predominantly negative
influence on children. While I agree that excessive television viewing can be harmful,
I believe that with proper guidance, it can also provide significant educational benefits.

On the one hand, critics of television point out that children who spend too much time
watching TV tend to perform poorly in school. Research has shown that passive screen
time reduces the amount of time available for reading, physical activity, and creative
play, all of which are essential for healthy development. Furthermore, exposure to
violent or inappropriate content can negatively affect children's behavior and attitudes.

On the other hand, not all television programming is harmful. Educational channels
such as documentaries and science programs can broaden children's knowledge about
the world. Programs designed specifically for young learners can help develop language
skills and introduce new concepts in an engaging way. When parents actively participate
by watching and discussing programs with their children, television can become a
valuable learning tool.

In conclusion, while the negative effects of excessive and unsupervised television
watching are well-documented, I believe the medium itself is not inherently damaging.
The key lies in parental involvement and careful selection of appropriate content.
Parents should set reasonable limits on screen time and encourage children to watch
educational programs that complement their schoolwork.
"""

SPEAKING_TRANSCRIPT = """
I think the most important invention of the twentieth century is definitely the internet.
Because it has changed everything in our life. Before internet people have to go to library
for find information, but now you can search anything in few seconds. Also internet help
people for communicate with friends and family who live in different countries.

I remember when I was child, my father go to post office for send letter to his brother
in another city. It take many days to arrive. But now we can video call immediately and
see each other face. This is very amazing thing.

Some people say mobile phone is more important, but I think internet is more big invention
because mobile phone also need internet for many functions. Without internet, mobile phone
is just for calling. So internet is the base of modern technology I think.

The bad side of internet is that some children spend too many time on social media and
they don't study. Parents must control this situation. But overall, internet bring more
benefit than problem for society.
"""


async def test_writing_task1():
    print("\n" + "="*60)
    print("TEST 1: Writing Task 1 (Academic)")
    print("="*60)
    word_count = count_words(TASK1_ESSAY)
    task_type = detect_writing_task_type(TASK1_ESSAY)
    valid, msg = validate_writing_text(TASK1_ESSAY)
    print(f"  Words: {word_count} | Task type: {task_type} | Valid: {valid}")
    assert valid, f"Validation failed: {msg}"
    assert task_type == "task1", f"Expected task1, got {task_type}"

    groq = GroqService(settings.groq_api_key)
    agent = WritingAgent(groq)
    feedback, model, elapsed = await agent.analyze(TASK1_ESSAY, task_type)

    print(f"  Model: {model} | Time: {elapsed}ms")
    print(f"  TA={feedback.task_achievement} CC={feedback.coherence_cohesion} "
          f"LR={feedback.lexical_resource} GRA={feedback.grammatical_accuracy}")
    print(f"  Overall: {feedback.overall_band}/9")
    print(f"  Errors found: {len(feedback.errors)}")
    print(f"  Strength: {feedback.strength_uz[:80]}...")
    print(f"  Suggestions: {len(feedback.suggestions_uz)}")

    assert 3.0 <= feedback.overall_band <= 9.0, f"Band score unrealistic: {feedback.overall_band}"
    assert feedback.corrected_text, "No corrected text"
    assert feedback.strength_uz, "No strength feedback in Uzbek"
    print("  ✅ PASSED")
    return feedback


async def test_writing_task2():
    print("\n" + "="*60)
    print("TEST 2: Writing Task 2 (Essay)")
    print("="*60)
    word_count = count_words(TASK2_ESSAY)
    task_type = detect_writing_task_type(TASK2_ESSAY)
    valid, msg = validate_writing_text(TASK2_ESSAY)
    print(f"  Words: {word_count} | Task type: {task_type} | Valid: {valid}")
    assert valid, f"Validation failed: {msg}"
    assert task_type == "task2", f"Expected task2, got {task_type}"

    groq = GroqService(settings.groq_api_key)
    agent = WritingAgent(groq)
    feedback, model, elapsed = await agent.analyze(TASK2_ESSAY, task_type)

    print(f"  Model: {model} | Time: {elapsed}ms")
    print(f"  TR={feedback.task_achievement} CC={feedback.coherence_cohesion} "
          f"LR={feedback.lexical_resource} GRA={feedback.grammatical_accuracy}")
    print(f"  Overall: {feedback.overall_band}/9")
    print(f"  Errors: {len(feedback.errors)}")
    print(f"  Weakness: {feedback.weakness_uz[:80]}...")

    assert 4.0 <= feedback.overall_band <= 9.0, f"Band score unrealistic: {feedback.overall_band}"
    assert feedback.corrected_text, "No corrected text"
    print("  ✅ PASSED")
    return feedback


async def test_speaking():
    print("\n" + "="*60)
    print("TEST 3: Speaking Analysis")
    print("="*60)
    word_count = count_words(SPEAKING_TRANSCRIPT)
    print(f"  Transcript words: {word_count} | Duration: ~90s")

    groq = GroqService(settings.groq_api_key)
    agent = SpeakingAgent(groq)
    feedback, model, elapsed = await agent.analyze(SPEAKING_TRANSCRIPT, 90.0)

    print(f"  Model: {model} | Time: {elapsed}ms")
    print(f"  FC={feedback.fluency_coherence} LR={feedback.lexical_resource} "
          f"GRA={feedback.grammatical_accuracy} P={feedback.pronunciation}")
    print(f"  Overall: {feedback.overall_band}/9")
    print(f"  Errors: {len(feedback.errors)}")
    print(f"  Strength: {feedback.strength_uz[:80]}...")

    assert 3.0 <= feedback.overall_band <= 8.0, f"Band score unrealistic: {feedback.overall_band}"
    assert feedback.corrected_transcript, "No corrected transcript"
    print("  ✅ PASSED")
    return feedback


async def test_validators():
    print("\n" + "="*60)
    print("TEST 4: Validators (error handling)")
    print("="*60)
    # Too short
    valid, msg = validate_writing_text("Hello world")
    assert not valid and "qisqa" in msg, f"Should fail for short text: {msg}"
    print(f"  Too short → '{msg}' ✅")

    # Non-English (50+ words in Russian Cyrillic)
    russian_text = "Привет я хочу написать эссе на английском языке но пока не умею потому что это очень трудно для меня " * 3
    valid, msg = validate_writing_text(russian_text)
    assert not valid, "Should fail for non-English"
    print(f"  Non-English (Cyrillic) → '{msg}' ✅")

    # Valid text (60+ words in English)
    valid, msg = validate_writing_text("The chart shows the number of students who attended university courses each year " * 4)
    assert valid, f"Should pass: {msg}"
    print(f"  Valid text → passed ✅")
    print("  ✅ ALL PASSED")


async def test_mongodb():
    print("\n" + "="*60)
    print("TEST 5: MongoDB Connection")
    print("="*60)
    db = MongoDBService(settings.mongodb_uri)
    await db.setup_indexes()

    user = await db.get_or_create_user(999999999, "test_user", "Test")
    assert user["telegram_id"] == 999999999
    print(f"  User created/found: {user['telegram_id']} ✅")

    stats = await db.get_user_stats(999999999)
    assert "total_submissions" in stats
    print(f"  Stats: {stats} ✅")

    rate_ok = await db.check_rate_limit(999999999)
    assert rate_ok
    print(f"  Rate limit: {rate_ok} ✅")

    await db.close()
    print("  ✅ PASSED")


async def test_formatters(w1_feedback, w2_feedback, sp_feedback):
    print("\n" + "="*60)
    print("TEST 6: Response Formatters")
    print("="*60)
    w1_text = format_writing_feedback(w1_feedback, 160)
    assert "IELTS Writing" in w1_text
    assert str(w1_feedback.overall_band) in w1_text
    print(f"  Writing T1 formatter: {len(w1_text)} chars ✅")

    w2_text = format_writing_feedback(w2_feedback, 280)
    assert len(w2_text) < 4100, f"Too long for Telegram: {len(w2_text)}"
    print(f"  Writing T2 formatter: {len(w2_text)} chars ✅")

    sp_text = format_speaking_feedback(sp_feedback, 90.0)
    assert "IELTS Speaking" in sp_text
    print(f"  Speaking formatter: {len(sp_text)} chars ✅")
    print("  ✅ ALL PASSED")


async def main():
    print("\nBZUF IELTS Bot -- Full Test Suite")
    print("="*60)

    try:
        await test_validators()
        await test_mongodb()
        w1 = await test_writing_task1()
        w2 = await test_writing_task2()
        sp = await test_speaking()
        await test_formatters(w1, w2, sp)

        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print(f"\nWriting Task 1 band: {w1.overall_band}/9")
        print(f"Writing Task 2 band: {w2.overall_band}/9")
        print(f"Speaking band:       {sp.overall_band}/9")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
