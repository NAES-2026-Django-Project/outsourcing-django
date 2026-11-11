"""Gera app.local.yaml (ignorado pelo git) a partir de app.yaml e dos segredos do .env."""

import json
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
DESTINO = BASE_DIR / 'app.local.yaml'


def main():
    environ.Env.read_env(BASE_DIR / '.env')
    env = environ.Env()
    variaveis = {
        'SECRET_KEY': env('SECRET_KEY'),
        'DATABASE_URL': env('DATABASE_URL'),
        'ANTHROPIC_API_KEY': env('ANTHROPIC_API_KEY', default=''),
        'DEBUG': 'False',
        'ALLOWED_HOSTS': '.appspot.com',
        'CSRF_TRUSTED_ORIGINS': 'https://*.appspot.com',
    }
    linhas = [(BASE_DIR / 'app.yaml').read_text().rstrip(), '', 'env_variables:']
    linhas += [f'  {nome}: {json.dumps(valor)}' for nome, valor in variaveis.items()]
    DESTINO.write_text('\n'.join(linhas) + '\n')
    DESTINO.chmod(0o600)
    print(f'Gerado: {DESTINO.name}')


if __name__ == '__main__':
    main()
