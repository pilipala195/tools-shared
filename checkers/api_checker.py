# Copyright 2025 The Lynx Authors. All rights reserved.
# Licensed under the Apache License Version 2.0 that can be found in the
# LICENSE file in the root directory of this source tree.

import os
import subprocess

from checkers.checker import Checker, CheckResult

LYNX_ROOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
ANDROID_PATH = 'platform/android/lynx_android/src/main'
IOS_PATH = 'platform/darwin/ios/lynx'
IOS_COMMON_PATH = 'platform/darwin/common/lynx'


class APIChecker(Checker):
    name = 'api-check'
    help = 'Update api metadata'

    def run(self, options, mr, changed_files):
        if self.skip(options, mr, changed_files):
            return CheckResult.PASSED

        cmd = [
            os.path.join(LYNX_ROOT_PATH, 'tools/vpython'),
            os.path.join(LYNX_ROOT_PATH, 'tools', 'api', 'main.py'), '-u'
        ]
        try:
            result = subprocess.run(cmd,
                                    text=True,
                                    check=True,
                                    cwd=LYNX_ROOT_PATH)
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            return CheckResult.FAILED

        cmd = ['git', 'diff', '--name-only']
        result = subprocess.run(cmd,
                                capture_output=True,
                                text=True,
                                check=True)
        if len(result.stdout) > 0 and ('lynx_android.api' in result.stdout
                                       or 'lynx_ios.api' in result.stdout):
            print('Found files possibly not containing proper api metadata.')
            print(result.stdout)
            print(
                'Please run "git status" or "git diff" to check local changes. You can "git add" these files and commit again.'
            )
            print(
                'If there are false positives or any other unexpected issues , please kindly inform yangguangzhao.solace@bytedance.com the situation so that we shall improve it.'
            )
            print('Sorry for your trouble. Appreciate your help.')

            return CheckResult.FAILED
        else:
            return CheckResult.PASSED

    def skip(self, options, mr, changed_files) -> bool:
        changed_files = [
            file for file in changed_files
            if (ANDROID_PATH in file and file.endswith('.java')) or (
                (IOS_PATH in file or IOS_COMMON_PATH in file)
                and file.endswith('.h')) or file.endswith('.api')
        ]
        if len(changed_files) == 0:
            print(
                'No changed files related with lynx native api, skip api check'
            )
            return True
        return False
