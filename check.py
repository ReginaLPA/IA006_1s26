import argparse
import json
from pathlib import Path

from src.health_core import collect_health_check, format_text_report


def main():
    parser = argparse.ArgumentParser(
        description="Health check do ambiente Python/JupyterLab."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Executa diagnóstico completo: pacotes, pastas, proxy, rede e Ollama."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Exibe saída em JSON."
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Salva o relatório em um arquivo .txt ou .json."
    )

    args = parser.parse_args()

    data = collect_health_check(full=args.full)

    if args.json:
        output = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        output = format_text_report(data)

    print(output)

    if args.save:
        path = Path(args.save)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
        print(f"\nArquivo salvo em: {path}")


if __name__ == "__main__":
    main()