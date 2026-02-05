from django.core.management.base import BaseCommand
from mitaina.models import Post


def strip_suffix(text: str) -> str:
    if not text:
        return text
    t = text.rstrip()
    if t.endswith("みたいな"):
        t = t[: -len("みたいな")].rstrip()
    return t


class Command(BaseCommand):
    help = "Strip trailing 'みたいな' from Post.text"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry = options["dry_run"]
        qs = Post.objects.all()
        changed = 0

        for p in qs.iterator():
            new_text = strip_suffix(p.text)
            if new_text != (p.text or ""):
                changed += 1
                if not dry:
                    p.text = new_text
                    p.save(update_fields=["text"])
        self.stdout.write(self.style.SUCCESS(f"done. changed={changed}, dry_run={dry}"))
