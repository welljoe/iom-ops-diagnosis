"""IOM Operations Diagnosis Agent - Command Line Interface"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import os
import sys
import json
import subprocess
from pathlib import Path

console = Console()

# 获取当前 CLI 工具的基础路径
CLI_BASE_DIR = Path(__file__).parent.parent.parent
# Agent 核心脚本路径 (假设安装在同一环境或相对路径)
AGENT_SKILLS_DIR = Path("/workspace/skills")


@click.group()
@click.version_option(version="1.1.0", prog_name="iom-ops")
def main():
    """
    IOM Operations Diagnosis Agent - 专业 HMLV 制造企业运营诊断工具
    
    提供项目初始化、阶段门检查、问题界定、方法选择、逻辑审核、可视化生成等全流程能力。
    """
    pass


@main.command()
@click.option("--project-name", default="demo-project", help="项目名称")
@click.option("--output-dir", default=".", help="输出目录")
def init(project_name, output_dir):
    """
    初始化新的 IOM 诊断项目
    
    创建标准目录结构、台账文件和配置文件。
    """
    console.print(Panel.fit("[bold blue]Initializing IOM Project...[/bold blue]"))
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Creating project '{project_name}'...", total=None)
        
        # 调用底层初始化脚本
        script_path = AGENT_SKILLS_DIR / "manage-iom-engagement" / "scripts" / "init_workspace.py"
        if script_path.exists():
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), "--project-name", project_name],
                    capture_output=True,
                    text=True,
                    cwd=output_dir
                )
                if result.returncode == 0:
                    progress.update(task, completed=True)
                    console.print("[green]✓[/green] Project initialized successfully!")
                    console.print(f"   Location: {os.path.abspath(output_dir)}/{project_name}")
                else:
                    console.print(f"[red]Error:[/red] {result.stderr}")
            except Exception as e:
                console.print(f"[red]Error:[/red] {str(e)}")
        else:
            # Fallback: 模拟初始化
            progress.update(task, completed=True)
            console.print("[yellow]Warning:[/yellow] Core script not found, creating basic structure...")
            os.makedirs(os.path.join(output_dir, project_name, "state"), exist_ok=True)
            console.print("[green]✓[/green] Basic structure created.")


@main.command()
@click.option("--gate", type=click.Choice(["G0", "G1", "G2", "G3", "G4", "G5"]), default="G0", help="阶段门级别")
@click.option("--all-gates", is_flag=True, help="检查所有阶段门")
def check(gate, all_gates):
    """
    执行阶段门检查
    
    验证项目是否满足特定阶段门的准入条件。
    """
    if all_gates:
        console.print(Panel.fit("[bold magenta]Running All Gates Check (G0-G5)...[/bold magenta]"))
        args = ["--all"]
    else:
        console.print(Panel.fit(f"[bold magenta]Running Gate {gate} Check...[/bold magenta]"))
        args = ["--gate", gate]
    
    script_path = AGENT_SKILLS_DIR / "manage-iom-engagement" / "scripts" / "gate_check.py"
    
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)] + args,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green]✓[/green] Gate check PASSED")
                if result.stdout:
                    console.print(result.stdout)
            else:
                console.print("[red]✗[/red] Gate check FAILED")
                if result.stderr:
                    console.print(result.stderr)
                if result.stdout:
                    console.print(result.stdout)
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] Gate check script not found.")
        console.print("Please ensure the agent core scripts are installed.")


@main.command()
@click.option("--input-file", required=True, help="痛点分析输入文件")
@click.option("--output-file", default="hypothesis_map.md", help="假设映射输出文件")
def map_painpoints(input_file, output_file):
    """
    痛点到假设映射
    
    基于 HMLV 模式库，将用户痛点转化为结构化假设。
    """
    console.print(Panel.fit("[bold cyan]Mapping Pain Points to Hypotheses...[/bold cyan]"))
    
    script_path = AGENT_SKILLS_DIR / "frame-iom-problem" / "scripts" / "painpoint_mapper.py"
    
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--input", input_file, "--output", output_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Mapping completed: {output_file}")
            else:
                console.print(f"[red]Error:[/red] {result.stderr}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] Mapper script not found.")


@main.command()
@click.option("--tree-file", required=True, help="Issue Tree 文件")
def check_mece(tree_file):
    """
    MECE 原则检查
    
    验证问题分解是否符合 MECE（相互独立、完全穷尽）原则。
    """
    console.print(Panel.fit("[bold yellow]Checking MECE Compliance...[/bold yellow]"))
    
    script_path = AGENT_SKILLS_DIR / "frame-iom-problem" / "scripts" / "mece_checker.py"
    
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--tree", tree_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print("[green]✓[/green] MECE check PASSED")
                console.print(result.stdout)
            else:
                console.print("[red]✗[/red] MECE check FAILED")
                console.print(result.stderr)
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] MECE checker script not found.")


@main.command()
@click.option("--bottleneck-tags", multiple=True, help="瓶颈标签列表")
@click.option("--output-file", default="analysis_plan.md", help="分析计划输出文件")
def select_methods(bottleneck_tags, output_file):
    """
    方法选择器
    
    根据瓶颈标签自动推荐最小方法栈。
    """
    console.print(Panel.fit("[bold green]Selecting Methods...[/bold green]"))
    
    script_path = AGENT_SKILLS_DIR / "select-iom-methods" / "scripts" / "method_selector.py"
    
    if script_path.exists():
        try:
            tags_list = list(bottleneck_tags) if bottleneck_tags else ["OTD_delay"]
            result = subprocess.run(
                [sys.executable, str(script_path), "--tags", ",".join(tags_list), "--output", output_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Methods selected: {output_file}")
            else:
                console.print(f"[red]Error:[/red] {result.stderr}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] Method selector script not found.")


@main.command()
@click.option("--page-register", required=True, help="页面注册表文件")
@click.option("--output-dir", default="outputs/pages", help="输出目录")
def render(page_register, output_dir):
    """
    渲染可视化页面
    
    根据页面注册表生成单页可视化内容。
    """
    console.print(Panel.fit("[bold blue]Rendering Pages...[/bold blue]"))
    
    script_path = AGENT_SKILLS_DIR / "generate-iom-visuals" / "scripts" / "render_page.py"
    
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--register", page_register, "--output", output_dir],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Pages rendered to: {output_dir}")
            else:
                console.print(f"[red]Error:[/red] {result.stderr}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] Render script not found.")


@main.command()
@click.option("--project-dir", default=".", help="项目目录")
@click.option("--output-dir", default="outputs/review", help="审阅包输出目录")
def build_pack(project_dir, output_dir):
    """
    构建审阅包
    
    组装完整 PPT 交付物和证据链文档。
    """
    console.print(Panel.fit("[bold magenta]Building Review Pack...[/bold magenta]"))
    
    script_path = AGENT_SKILLS_DIR / "produce-iom-deck" / "scripts" / "build_review_pack.py"
    
    if script_path.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--project", project_dir, "--output", output_dir],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓[/green] Review pack built: {output_dir}")
                console.print(result.stdout)
            else:
                console.print(f"[red]Error:[/red] {result.stderr}")
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
    else:
        console.print("[yellow]Warning:[/yellow] Build script not found.")


@main.command()
def status():
    """
    显示当前项目状态
    
    展示阶段门进度、台账摘要和待办事项。
    """
    console.print(Panel.fit("[bold white]Project Status[/bold white]"))
    
    table = Table(title="Current State")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # 模拟状态信息
    table.add_row("Current Gate", "G0 - Pending")
    table.add_row("Active Hypotheses", "0")
    table.add_row("Evidence Count", "0")
    table.add_row("Pages Generated", "0")
    
    console.print(table)
    
    console.print("\n[yellow]Note:[/yellow] Initialize a project first using 'iom-ops init'")


if __name__ == "__main__":
    main()
