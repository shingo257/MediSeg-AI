"""
依存関係チェック共通モジュール
パッケージの存在確認とインストール機能を提供
"""

import sys
import subprocess
from typing import List, Optional, Tuple


def check_dependencies(packages: List[str]) -> List[str]:
    """
    依存関係のチェック
    
    Args:
        packages: チェックするパッケージ名のリスト
        
    Returns:
        見つからないパッケージ名のリスト
    """
    missing_packages = []
    
    for package in packages:
        try:
            # パッケージ名のハイフンをアンダースコアに変換（例: opencv-python -> opencv_python）
            module_name = package.replace('-', '_')
            __import__(module_name)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages


def install_dependencies(packages: List[str], verbose: bool = True) -> bool:
    """
    依存関係のインストール
    
    Args:
        packages: インストールするパッケージ名のリスト
        verbose: 詳細な出力を行うかどうか
        
    Returns:
        インストールが成功したかどうか
    """
    if not packages:
        return True
    
    if verbose:
        print(f"Installing missing packages: {', '.join(packages)}")
    
    for package in packages:
        try:
            if verbose:
                print(f"Installing {package}...")
            subprocess.check_call(
                [sys.executable, '-m', 'pip', 'install', package],
                stdout=subprocess.DEVNULL if not verbose else None,
                stderr=subprocess.DEVNULL if not verbose else None
            )
            if verbose:
                print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            if verbose:
                print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True


def check_and_install_dependencies(
    packages: List[str],
    auto_install: bool = True,
    verbose: bool = True
) -> Tuple[bool, List[str]]:
    """
    依存関係のチェックと必要に応じてインストール
    
    Args:
        packages: チェックするパッケージ名のリスト
        auto_install: 見つからないパッケージを自動インストールするかどうか
        verbose: 詳細な出力を行うかどうか
        
    Returns:
        (成功したかどうか, 見つからなかったパッケージのリスト)
    """
    missing = check_dependencies(packages)
    
    if not missing:
        return True, []
    
    if verbose:
        print(f"❌ Missing packages: {', '.join(missing)}")
    
    if auto_install:
        if install_dependencies(missing, verbose=verbose):
            return True, []
        else:
            return False, missing
    
    return False, missing

