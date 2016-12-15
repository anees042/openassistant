import logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

from argparse import ArgumentParser, Namespace

import os
import signal
import sys
import subprocess
from pocketsphinx import LiveSpeech, get_model_path

from core import Config, Assistant

from modules.language import LanguageUpdater

def _parser(args):
    parser = ArgumentParser()

    parser.add_argument("-c", "--continuous",
            action="store_true", dest="continuous", default=False,
            help="Start interface with 'continuous' listen enabled")

    parser.add_argument("-p", "--pass-words",
            action="store_true", dest="pass_words", default=False,
            help="Pass the recognized words as arguments to the shell" +
            " command")

    parser.add_argument("-H", "--history", type=int,
            action="store", dest="history",
            help="Number of commands to store in history file")

    parser.add_argument("-m", "--microphone", type=int,
            action="store", dest="microphone", default=None,
            help="Audio input card to use (if other than system default)")

    parser.add_argument("--valid-sentence-command", type=str,
            dest="valid_sentence_command", action='store',
            help="Command to run when a valid sentence is detected")

    parser.add_argument("--invalid-sentence-command", type=str,
            dest="invalid_sentence_command", action='store',
            help="Command to run when an invalid sentence is detected")

    parser.add_argument("-M", "--mind", type=str,
            dest="mind_dir", action='store',
            help="Path to mind to use for assistant")

    return parser.parse_args(args)


def recognizer_finished(a, recognizer, text):
    logger.debug("Agent: {}, Recognier: {}, Text: {}".format(a, recognizer, text))
    t = text.lower()
    #numt, nums = self.number_parser.parse_all_numbers(t)
    # Is There A Matching Command?
    if t in a.config.commands:
        # Run The 'valid_sentence_command' If It's Set
        os.system('clear')
        print("Open Assistant: \x1b[32mListening\x1b[0m")
        if a.config.options['valid_sentence_command']:
            subprocess.call(a.config.options['valid_sentence_command'],
                            shell=True)
        cmd = a.config.commands[t]
        # Should We Be Passing Words?
        os.system('clear')
        print("Open Assistant: \x1b[32mListening\x1b[0m")
        if a.config.options['pass_words']:
            cmd += " " + t
        print("\x1b[32m< ! >\x1b[0m {0}".format(t))
        run_command(a, cmd)
        log_history(a, text)
    #elif numt in self.commands:
    #    # Run 'valid_sentence_command' Set
    #    os.system('clear')
    #    print("Open Assistant: \x1b[32mListening\x1b[0m")
    #    if self.config.options['valid_sentence_command']:
    #        subprocess.call(self.config.options['valid_sentence_command'],
    #                        shell=True)
    #    cmd = self.commands[numt]
    #    cmd = cmd.format(*nums)
    #    # Should We Be Passing Words?
    #    if self.config.options['pass_words']:
    #        cmd += " " + t
    #    print("\x1b[32m< ! >\x1b[0m {0}".format(t))
    #    self.run_command(cmd)
    #    self.log_history(text)
    else:
        # Run The Invalid_sentence_command If It's Set
        if a.config.options['invalid_sentence_command']:
            subprocess.call(a.config.options['invalid_sentence_command'],
                            shell=True)
        print("\x1b[31m< ? >\x1b[0m {0}".format(t))


def log_history(a, text):
    if a.config.options['history']:
        a.history.append(text)
        if len(a.history) > a.config.options['history']:
            # Pop Off First Item
            a.history.pop(0)

        # Open And Truncate History File
        with open(a.config.history_file, 'w') as hfile:
            for line in a.history:
                hfile.write(line + '\n')


def run_command(a, cmd):
    """PRINT COMMAND AND RUN"""
    print("\x1b[32m< ! >\x1b[0m", cmd)
    recognizer.pause()
    subprocess.call(cmd, shell=True)
    recognizer.listen()


def process_command(self, command):
    print(command)
    if command == "listen":
        self.recognizer.listen()
    elif command == "stop":
        self.recognizer.pause()
    elif command == "continuous_listen":
        self.continuous_listen = True
        self.recognizer.listen()
    elif command == "continuous_stop":
        self.continuous_listen = False
        self.recognizer.pause()
    elif command == "quit":
        self.quit()


def main():
    model_path = get_model_path()
    #print (model_path)
    speech = LiveSpeech(
        verbose=False,
        sampling_rate=16000,
        buffer_size=2048,
        no_search=False,
        full_utt=False,
        hmm=os.path.join(model_path, 'en-us'),
        lm=os.path.join(model_path, 'en-us.lm.bin'),
        dic=os.path.join(model_path, 'cmudict-en-us.dict')
    )

    for phrase in speech:
        print(phrase)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Killed by user')
        sys.exit(0)
