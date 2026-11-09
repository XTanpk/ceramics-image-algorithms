"""Verify and stream release parts directly into docker load; no joined archive needed."""
import argparse
import hashlib
import json
import pathlib
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', default='.', help='Directory containing downloaded release files')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    directory = pathlib.Path(args.directory)
    manifest = json.loads((directory/'images.json').read_text(encoding='utf-8'))
    for part in manifest['parts']:
        path = directory / part['name']
        if path.stat().st_size != part['size']:
            raise SystemExit('Incorrect size: '+part['name'])
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for chunk in iter(lambda: source.read(8*1024*1024), b''):
                digest.update(chunk)
        if digest.hexdigest() != part['sha256']:
            raise SystemExit('Checksum mismatch: '+part['name'])
        print('Verified', part['name'], flush=True)
    if args.verify_only:
        return
    process = subprocess.Popen(['docker', 'load'], stdin=subprocess.PIPE)
    digest = hashlib.sha256()
    try:
        for part in manifest['parts']:
            with (directory/part['name']).open('rb') as source:
                for chunk in iter(lambda: source.read(8*1024*1024), b''):
                    digest.update(chunk)
                    process.stdin.write(chunk)
        process.stdin.close()
        if process.wait() != 0:
            raise SystemExit('docker load failed')
    except BaseException:
        process.kill()
        process.wait()
        raise
    if digest.hexdigest() != manifest['archive']['sha256']:
        raise SystemExit('Combined archive checksum mismatch')
    for image in manifest['images']:
        actual = subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',image['image']],text=True).strip()
        if actual != image['config_digest']:
            raise SystemExit('Image digest mismatch: '+image['image'])
        print('Imported and verified', image['image'])

if __name__ == '__main__':
    main()
