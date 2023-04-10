#include "unity.h"
#include "controller.cpp"

using namespace bzzz;

void setUp(void)
{
    // set stuff up here
}

void tearDown(void)
{
    // clean stuff up here
}

void test_controller(void)
{
    float u = controlAction(0.0);
    bool condition = u > 0.0;
    TEST_ASSERT_TRUE(condition);
}

void test_another(void)
{
    float u = bzzz::controlAction(1.0);
    Serial.print("u = ");
    Serial.println(u);
}

void test_yet_another(void)
{
    TEST_ASSERT_EQUAL_INT(1, 1);
}

int runUnityTests(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_controller);
    RUN_TEST(test_another);
    RUN_TEST(test_yet_another);
    return UNITY_END();
}

/**
 * For Arduino framework
 */
void setup()
{
    Serial.begin(115200);

    // Wait ~2 seconds before the Unity test runner
    // establishes connection with a board Serial interface
    delay(2000);

    runUnityTests();
}

void loop() {}

/**
 * For ESP-IDF framework
 */
void app_main()
{
    runUnityTests();
}