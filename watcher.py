from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import subprocess
import time


def run_command(cmd):
    print(f"\nRunning: {cmd}\n")
    subprocess.run(cmd, shell=True)


class FileEventHandler(PatternMatchingEventHandler):
    def __init__(self, patterns, command):
        super().__init__(patterns=patterns)
        self.command = command

    def on_modified(self, event):
        run_command(self.command)

    def on_created(self, event):
        run_command(self.command)


if __name__ == "__main__":
    observer = Observer()

    # Watch input/*.dsl → run_generator.py
    input_handler = FileEventHandler(
        patterns=["*.dsl"], command="poetry run python run_generator.py"
    )
    observer.schedule(input_handler, path="input/", recursive=True)

    # Watch output/*.drawio → run_table_locator.py
    output_handler = FileEventHandler(
        patterns=["*.drawio"], command="poetry run python run_table_locator.py"
    )
    observer.schedule(output_handler, path="output/", recursive=True)

    observer.start()
    print("✅ Watching 'input/' for .dsl and 'output/' for .drawio changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 Stopped watcher.")

    observer.join()
