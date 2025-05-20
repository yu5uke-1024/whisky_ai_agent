# import uuid

# from dotenv import load_dotenv
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
# from google.genai import types
# from supervisor_agent import whisky_agent


# load_dotenv()

# # Create a new session service to store state
# session_service_stateful = InMemorySessionService()

# initial_state = {
#     "user_name": "山本 太郎",
#     "user_preferences": """
#     私はピクルボール、ディスクゴルフ、テニスをするのが好きです。
#     好きな食べ物はメキシコ料理です。
#     お気に入りのテレビ番組は『ゲーム・オブ・スローンズ』です。
#     YouTubeチャンネルに「いいね」や「チャンネル登録」してもらえるととても嬉しいです。
#     """,
# }


# # Create a NEW session
# APP_NAME = "Yamamoto Bot"
# USER_ID = "yamamoto_taro"
# SESSION_ID = str(uuid.uuid4())
# stateful_session = session_service_stateful.create_session(
#     app_name=APP_NAME,
#     user_id=USER_ID,
#     session_id=SESSION_ID,
#     state=initial_state,
# )
# print("CREATED NEW SESSION:")
# print(f"\tSession ID: {SESSION_ID}")

# runner = Runner(
#     agent=whisky_agent,
#     app_name=APP_NAME,
#     session_service=session_service_stateful,
# )

# new_message = types.Content(
#     role="user", parts=[types.Part(text="What is Yamamoto's favorite TV show?")]
# )

# for event in runner.run(
#     user_id=USER_ID,
#     session_id=SESSION_ID,
#     new_message=new_message,
# ):
#     if event.is_final_response():
#         if event.content and event.content.parts:
#             print(f"Final Response: {event.content.parts[0].text}")

# print("==== Session Event Exploration ====")
# session = session_service_stateful.get_session(
#     app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
# )

# # Log final Session state
# print("=== Final Session State ===")
# for key, value in session.state.items():
#     print(f"{key}: {value}")
