"""
Instagram OSINT Tool - Outil de collecte d'informations utilisateur
Thème "hacker" pour la console, reconnaissance Instagram
"""

import sys
import time
import instaloader
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from colorama import Fore, Style, init

# Colorama initialisation
init(autoreset=True)

console = Console()


def print_banner():
    """Afficher la bannière thème hacker"""
    banner = f"""
{Fore.GREEN}╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗███╗   ██╗███████╗████████╗ █████╗      ██████╗ ███████╗║
║   ██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗    ██╔═══██╗██╔════╝║
║   ██║██╔██╗ ██║███████╗   ██║   ███████║    ██║   ██║███████╗║
║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██║    ██║   ██║╚════██║║
║   ██║██║ ╚████║███████║   ██║   ██║  ██║    ╚██████╔╝███████║║
║   ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚══════╝║
║                                                               ║
║           Outil de renseignement Open Source Instagram         ║
║                    [ Données publiques uniquement ]           ║
╚═══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)
    time.sleep(0.5)


def typing_effect(text, color=Fore.GREEN, delay=0.03):
    """Afficher du texte avec effet de saisie"""
    for char in text:
        sys.stdout.write(color + char + Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def animate_loading(message, duration=2):
    """Afficher une animation de chargement"""
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[green]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(message, total=None)
        time.sleep(duration)


def format_number(num):
    """Formater les nombres (K, M ...)"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)


def get_profile_data(username):
    """Récupérer les données du profil Instagram"""
    try:
        typing_effect(f"[*] Cible: {username}", Fore.CYAN, 0.02)
        time.sleep(0.3)
        
        typing_effect("[*] Connexion au système...", Fore.YELLOW, 0.02)
        animate_loading("Accès aux serveurs Instagram en cours", 1.5)
        
        # Instance Instaloader
        L = instaloader.Instaloader()
        
        typing_effect("[*] Récupération des données du profil...", Fore.YELLOW, 0.02)
        animate_loading("Extraction des informations utilisateur", 1.8)
        
        # Charger le profil
        profile = instaloader.Profile.from_username(L.context, username)
        
        typing_effect("[*] Analyse des publications...", Fore.YELLOW, 0.02)
        animate_loading("Analyse des dernières publications", 1.5)
        
        # Récupérer les informations des posts
        posts_data = []
        post_count = 0
        try:
            for post in profile.get_posts():
                if post_count >= 10:  # Dernières 10 publications
                    break
                posts_data.append({
                    'date': post.date_local.strftime('%Y-%m-%d %H:%M'),
                    'likes': post.likes,
                    'comments': post.comments,
                    'caption': post.caption[:50] + '...' if post.caption and len(post.caption) > 50 else (post.caption or 'N/A'),
                    'type': post.typename
                })
                post_count += 1
        except Exception as e:
            console.print(f"[yellow]⚠ Impossible d'obtenir les données des publications (le profil peut être privé)[/yellow]")
        
        typing_effect("[✓] Collecte des données terminée !", Fore.GREEN, 0.02)
        time.sleep(0.5)
        
        return {
            'profile': profile,
            'posts': posts_data
        }
        
    except instaloader.exceptions.ProfileNotExistsException:
        console.print(f"[red]✗ Erreur: l'utilisateur '{username}' n'existe pas ![/red]")
        return None
    except instaloader.exceptions.ConnectionException:
        console.print("[red]✗ Erreur: Impossible de se connecter à Instagram ![/red]")
        return None
    except Exception as e:
        console.print(f"[red]✗ Erreur: {str(e)}[/red]")
        return None


def display_profile_info(data):
    """Afficher les informations du profil sous forme de tableau"""
    profile = data['profile']
    
    # Tableau d'informations du profil
    console.print("\n")
    profile_table = Table(
        title="[bold green]═══ INFORMATIONS DU PROFIL ═══[/bold green]",
        box=box.DOUBLE_EDGE,
        border_style="green",
        header_style="bold cyan",
        show_header=True,
        title_style="bold green"
    )
    
    profile_table.add_column("Paramètre", style="yellow", width=25)
    profile_table.add_column("Valeur", style="white", width=50)
    
    # Détails du profil
    profile_table.add_row("👤 Nom d'utilisateur", f"@{profile.username}")
    profile_table.add_row("📝 Nom complet", profile.full_name or "N/A")
    profile_table.add_row("🆔 ID utilisateur", str(profile.userid))
    profile_table.add_row("📊 Abonnés", f"[green]{format_number(profile.followers)}[/green]")
    profile_table.add_row("👥 Abonnements", f"[cyan]{format_number(profile.followees)}[/cyan]")
    profile_table.add_row("📸 Nombre de publications", f"[magenta]{profile.mediacount}[/magenta]")
    profile_table.add_row("✅ Vérifié", "✓ Oui" if profile.is_verified else "✗ Non")
    profile_table.add_row("🔒 Compte privé", "✓ Oui" if profile.is_private else "✗ Non")
    profile_table.add_row("💼 Compte professionnel", "✓ Oui" if profile.is_business_account else "✗ Non")
    
    if profile.biography:
        bio = profile.biography.replace('\n', ' ')[:100]
        profile_table.add_row("📋 Biographie", bio)
    
    if profile.external_url:
        profile_table.add_row("🔗 Site web", profile.external_url)
    
    profile_table.add_row("🖼️ Photo de profil", profile.profile_pic_url)
    
    console.print(profile_table)


def display_posts_info(data):
    """Afficher les informations des publications sous forme de tableau"""
    posts = data['posts']
    
    if not posts:
        console.print("\n[yellow]⚠ Aucune donnée de publication disponible (le profil peut être privé)[/yellow]")
        return
    
    console.print("\n")
    posts_table = Table(
        title="[bold green]═══ DERNIÈRES PUBLICATIONS ═══[/bold green]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        header_style="bold yellow",
        show_header=True,
        title_style="bold green"
    )
    
    posts_table.add_column("#", style="cyan", width=5, justify="center")
    posts_table.add_column("Date", style="yellow", width=18)
    posts_table.add_column("Type", style="magenta", width=12)
    posts_table.add_column("❤️ Likes", style="red", width=10, justify="right")
    posts_table.add_column("💬 Commentaires", style="blue", width=10, justify="right")
    posts_table.add_column("📝 Légende", style="white", width=40)
    
    for idx, post in enumerate(posts, 1):
        post_type = post['type'].replace('Graph', '')
        posts_table.add_row(
            str(idx),
            post['date'],
            post_type,
            format_number(post['likes']),
            format_number(post['comments']),
            post['caption']
        )
    
    console.print(posts_table)


def display_statistics(data):
    """Afficher le résumé des statistiques"""
    profile = data['profile']
    posts = data['posts']
    
    console.print("\n")
    stats_table = Table(
        title="[bold green]═══ RÉSUMÉ DES STATISTIQUES ═══[/bold green]",
        box=box.DOUBLE_EDGE,
        border_style="magenta",
        header_style="bold cyan",
        show_header=True,
        title_style="bold green"
    )
    
    stats_table.add_column("Métrique", style="yellow", width=30)
    stats_table.add_column("Valeur", style="white", width=45)
    
    # Calculs
    if posts:
        total_likes = sum(p['likes'] for p in posts)
        total_comments = sum(p['comments'] for p in posts)
        avg_likes = total_likes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        engagement_rate = ((total_likes + total_comments) / len(posts) / profile.followers * 100) if profile.followers > 0 else 0
        
        stats_table.add_row("📊 Nombre de publications analysées", str(len(posts)))
        stats_table.add_row("❤️ Total des likes", f"[red]{format_number(total_likes)}[/red]")
        stats_table.add_row("💬 Total des commentaires", f"[blue]{format_number(total_comments)}[/blue]")
        stats_table.add_row("📈 Moyenne likes/poste", f"[green]{format_number(int(avg_likes))}[/green]")
        stats_table.add_row("📊 Moyenne commentaires/poste", f"[cyan]{format_number(int(avg_comments))}[/cyan]")
        stats_table.add_row("🎯 Taux d'engagement", f"[magenta]{engagement_rate:.2f}%[/magenta]")
    
    # Ratio abonnés/abonnements
    if profile.followees > 0:
        follower_ratio = profile.followers / profile.followees
        stats_table.add_row("📊 Ratio abonnés/abonnements", f"[yellow]{follower_ratio:.2f}[/yellow]")
    
    console.print(stats_table)


def main():
    """Programme principal"""
    try:
        print_banner()
        
        typing_effect("\n[>] Outil OSINT Instagram démarré...", Fore.GREEN, 0.02)
        time.sleep(0.5)
        
        # Obtenir le nom d'utilisateur
        username = console.input("\n[bold cyan][?] Entrez le nom d'utilisateur cible :[/bold cyan] ").strip()
        
        if not username:
            console.print("[red]✗ Le nom d'utilisateur ne peut pas être vide ![/red]")
            return
        
        print("\n" + "="*70)
        
        # Récupérer les données
        data = get_profile_data(username)
        
        if data:
            print("\n" + "="*70)
            typing_effect("\n[✓] Préparation des données...", Fore.GREEN, 0.02)
            time.sleep(0.5)
            
            # Afficher les tableaux
            display_profile_info(data)
            display_posts_info(data)
            display_statistics(data)
            
            # Message final
            console.print("\n" + "="*70)
            console.print(Panel(
                "[bold green]✓ Analyse terminée ![/bold green]\n"
                "[yellow]Les données collectées sont affichées à l'écran.[/yellow]",
                border_style="green",
                box=box.DOUBLE
            ))
            
    except KeyboardInterrupt:
        console.print("\n\n[red]✗ Opération interrompue par l'utilisateur ![/red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]✗ Erreur inattendue: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
