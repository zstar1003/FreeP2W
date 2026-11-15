"""Fail-safe CLI output publication (the input PDF must never be replaced)."""
from contextlib import contextmanager
import os
import tempfile


def validate_output_path(pdf_path, output_path, overwrite=False):
    if os.path.realpath(pdf_path) == os.path.realpath(output_path):
        raise ValueError('输出路径不能与输入 PDF 相同')
    if os.path.exists(output_path) and os.path.samefile(pdf_path, output_path):
        raise ValueError('输出路径不能指向输入 PDF（包括硬链接）')
    if os.path.isdir(output_path):
        raise ValueError('输出路径是目录')
    if os.path.lexists(output_path) and not overwrite:
        raise FileExistsError('输出文件已存在；请选择新文件名或使用 --overwrite')


@contextmanager
def safe_output(pdf_path, output_path, overwrite=False):
    """Stage beside the destination; publish only after conversion succeeds.

    Default publication uses an atomic no-clobber hard link. Filesystems without
    hard-link support fail safely instead of falling back to a racy overwrite.
    """
    validate_output_path(pdf_path, output_path, overwrite)
    directory = os.path.dirname(os.path.abspath(output_path))
    fd, staged = tempfile.mkstemp(prefix='.freep2w-', suffix='.docx', dir=directory)
    os.close(fd)
    try:
        yield staged
        validate_output_path(pdf_path, output_path, overwrite)
        if overwrite:
            os.replace(staged, output_path)
        else:
            os.link(staged, output_path)
    finally:
        if os.path.exists(staged):
            os.unlink(staged)
