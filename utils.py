from datetime import datetime
import base64
from google.genai import types


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


async def update_interaction_history(session_service, app_name, user_id, session_id, entry):
    """Add an entry to the interaction history in state.

    Args:
        session_service: The session service instance
        app_name: The application name
        user_id: The user ID
        session_id: The session ID
        entry: A dictionary containing the interaction data
            - requires 'action' key (e.g., 'user_query', 'agent_response')
            - other keys are flexible depending on the action type
    """
    try:
        # Get current session
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Get current interaction history
        interaction_history = session.state.get("interaction_history", [])

        # Add timestamp if not already present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the entry to interaction history
        interaction_history.append(entry)

        # Create updated state
        updated_state = session.state.copy()
        updated_state["interaction_history"] = interaction_history

        # Create a new session with updated state
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=updated_state,
        )

        # Firestoreに状態を保存
        try:
            from whisky_agent.storage.firestore import FirestoreClient
            firestore_client = FirestoreClient()
            firestore_client.save_session_with_id(user_id, session_id, updated_state)
        except Exception as firestore_error:
            print(f"Failed to save state to Firestore: {firestore_error}")

        # LINEボット環境でローカルステートキャッシュを更新
        try:
            from line_bot_server import user_session_states
            user_session_states[user_id] = updated_state
            print(f"Updated local session state cache for user {user_id}")
        except ImportError:
            # main.py環境では無視
            pass

    except Exception as e:
        print(f"Error updating interaction history: {e}")



async def add_user_query_to_history(session_service, app_name, user_id, session_id, query):
    """Add a user query to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "user_query",
            "query": query,
        },
    )


async def add_agent_response_to_history(
    session_service, app_name, user_id, session_id, agent_name, response
):
    """Add an agent response to the interaction history."""
    await update_interaction_history(
        session_service,
        app_name,
        user_id,
        session_id,
        {
            "action": "agent_response",
            "agent": agent_name,
            "response": response,
        },
    )


async def display_state(
    session_service, app_name, user_id, session_id, label="Current State"
):
    """Display the current session state in a formatted way."""
    try:
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )

        # Format the output with clear sections
        print(f"\n{'-' * 10} {label} {'-' * 10}")


        # Handle interaction history in a more readable way
        interaction_history = session.state.get("interaction_history", [])
        if interaction_history:
            print("📝 Interaction History:")
            for idx, interaction in enumerate(interaction_history, 1):
                # Pretty format dict entries, or just show strings
                if isinstance(interaction, dict):
                    action = interaction.get("action", "interaction")
                    timestamp = interaction.get("timestamp", "unknown time")

                    if action == "user_query":
                        query = interaction.get("query", "")
                        print(f'  {idx}. User query at {timestamp}: "{query}"')
                    elif action == "agent_response":
                        agent = interaction.get("agent", "unknown")
                        response = interaction.get("response", "")
                        print(f'  {idx}. {agent} response at {timestamp}: "{response}"')
                    else:
                        details = ", ".join(
                            f"{k}: {v}"
                            for k, v in interaction.items()
                            if k not in ["action", "timestamp"]
                        )
                        print(
                            f"  {idx}. {action} at {timestamp}"
                            + (f" ({details})" if details else "")
                        )
                else:
                    print(f"  {idx}. {interaction}")
        else:
            print("📝 Interaction History: None")

        # Show any additional state keys that might exist
        other_keys = [
            k
            for k in session.state.keys()
            if k not in ["interaction_history"]
        ]
        if other_keys:
            print("🔑 Additional State:")
            for key in other_keys:
                print(f"  {key}: {session.state[key]}")

        print("-" * (22 + len(label)))
    except Exception as e:
        print(f"Error displaying state: {e}")


async def process_agent_response(event):
    """Process and display agent response events."""
    # Only process and display the final response
    if event.is_final_response():
        if (
            event.content
            and event.content.parts
            and hasattr(event.content.parts[0], "text")
            and event.content.parts[0].text
        ):
            final_response = event.content.parts[0].text.strip()
            # Use colors and formatting to make the final response stand out
            print(
                f"\n{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╔══ AGENT RESPONSE ═════════════════════════════════════════{Colors.RESET}"
            )
            print(f"{Colors.CYAN}{Colors.BOLD}{final_response}{Colors.RESET}")
            print(
                f"{Colors.BG_BLUE}{Colors.WHITE}{Colors.BOLD}╚═════════════════════════════════════════════════════════════{Colors.RESET}\n"
            )
            return final_response
        else:
            print(
                f"\n{Colors.BG_RED}{Colors.WHITE}{Colors.BOLD}==> Final Agent Response: [No text content in final event]{Colors.RESET}\n"
            )
            return None

    return None

def create_content_parts(query: str, image_path: str = None):
    parts = [types.Part(text=query)]
    if image_path:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            parts.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",  # or image/png
                        data=image_b64,
                    )
                )
            )
    return parts

async def call_agent_async(runner, user_id, session_id, query:str, image_path:str = None):
    """Call the agent asynchronously with the user's query."""
    parts = create_content_parts(query, image_path)
    content = types.Content(role="user", parts=parts)
    print(
        f"\n{Colors.BG_GREEN}{Colors.BLACK}{Colors.BOLD}--- Running Query: {query} ---{Colors.RESET}"
    )
    final_response_text = None
    agent_name = None

    # Display state before processing the message
    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State BEFORE processing",
    )

    try:
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # Capture the agent name from the event if available
            if event.author:
                agent_name = event.author

            response = await process_agent_response(event)
            if response:
                final_response_text = response
    except Exception as e:
        print(f"{Colors.BG_RED}{Colors.WHITE}ERROR during agent run: {e}{Colors.RESET}")

    # Add the agent response to interaction history if we got a final response
    if final_response_text and agent_name:
        await add_agent_response_to_history(
            runner.session_service,
            runner.app_name,
            user_id,
            session_id,
            agent_name,
            final_response_text,
        )

    # Display state after processing the message
    await display_state(
        runner.session_service,
        runner.app_name,
        user_id,
        session_id,
        "State AFTER processing",
    )

    print(f"{Colors.YELLOW}{'-' * 30}{Colors.RESET}")
    return final_response_text


async def create_or_get_session(session_service, app_name, user_id):
    """セッションを作成または取得する共通関数"""

    # Firestoreから既存の状態を取得を試みる
    try:
        from whisky_agent.storage.firestore import FirestoreClient
        firestore_client = FirestoreClient()
        existing_session_id, existing_state = firestore_client.get_session_with_id(user_id)

        if existing_session_id and existing_state:
            print(f"Found existing session in Firestore for user {user_id}: {existing_session_id}")
            # 既存セッションを復元
            session = await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=existing_session_id,
                state=existing_state,
            )
            print(f"Session restored: ID={session.id}, User={user_id}")
            return session
    except Exception as e:
        print(f"Failed to load existing session from Firestore: {e}")

    # 新しいセッションを作成
    initial_state = {
        "interaction_history": [],
    }

    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        state=initial_state,
    )

    # 新しいセッションをFirestoreに保存
    try:
        from whisky_agent.storage.firestore import FirestoreClient
        firestore_client = FirestoreClient()
        firestore_client.save_session_with_id(user_id, session.id, initial_state)
    except Exception as e:
        print(f"Failed to save new session to Firestore: {e}")

    print(f"New session created: ID={session.id}, User={user_id}, State={session.state}")
    return session


async def initialize_whisky_agent_system(session_service, artifact_service, app_name="Whisky Assistant"):
    """Whisky Agent システムを初期化する共通関数"""
    from google.adk.runners import Runner
    from whisky_agent.agent import root_agent

    print(f"Initializing Whisky Agent system with app_name: {app_name}")

    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    print("Whisky Agent system initialized successfully")
    return runner
