"""
DomusAI - Sistema de Generación de Reportes

Este módulo implementa la generación automática de reportes mensuales de
consumo energético en formato HTML y PDF.

Características:
- Generación de reportes mensuales completos
- Integración con predictor.py y anomalies.py
- Gráficos embebidos automáticos
- Templates personalizables con Jinja2
- Exportación a HTML y PDF

Autor: DomusAI Team
Fecha: Octubre 2025
Versión: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import logging
import os

# Importar xhtml2pdf para exportación PDF (compatible con Windows)
try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("⚠️ xhtml2pdf no disponible - exportación PDF deshabilitada")

# Configurar matplotlib para mejor calidad
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/reporting.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    🔮 Generador de Reportes Automáticos DomusAI
    
    Genera reportes mensuales profesionales integrando datos históricos,
    predicciones y detección de anomalías.
    
    Attributes:
        template_dir (str): Directorio de templates Jinja2
        assets_dir (str): Directorio de assets (logo, iconos)
        output_dir (str): Directorio de reportes generados
        
    Example:
        >>> generator = ReportGenerator()
        >>> report = generator.generate_monthly_report(
        ...     data=df,
        ...     predictions=pred_dict,
        ...     anomalies=anom_dict
        ... )
        >>> print(f"Reporte generado: {report['html_path']}")
    """
    
    def __init__(
        self,
        template_dir: str = 'reports/templates',
        assets_dir: str = 'reports/assets',
        output_dir: str = 'reports/generated'
    ):
        """
        Inicializar generador de reportes.
        
        Args:
            template_dir: Directorio con templates HTML
            assets_dir: Directorio con assets (logo, iconos)
            output_dir: Directorio para guardar reportes generados
        """
        self.template_dir = Path(template_dir)
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        
        # Crear directorio de salida si no existe
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir))
        )
        
        logger.info(f"🔧 ReportGenerator inicializado")
        logger.info(f"   Templates: {self.template_dir}")
        logger.info(f"   Output: {self.output_dir}")
    
    
    def generate_monthly_report(
        self,
        data: pd.DataFrame,
        predictions: Optional[Dict] = None,
        anomalies: Optional[Dict] = None,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """
        🎯 FUNCIÓN PRINCIPAL - Generar reporte mensual completo.
        
        Args:
            data: DataFrame con datos históricos de consumo
            predictions: Dict con predicciones de predictor.predict()
            anomalies: Dict con anomalías de anomalies.detect()
            month: Mes del reporte (default: mes actual)
            year: Año del reporte (default: año actual)
            
        Returns:
            Dict con rutas de archivos generados y metadata:
                {
                    'html_path': str,
                    'pdf_path': str (si se genera),
                    'charts': Dict[str, str],
                    'summary': Dict,
                    'status': str,
                    'generation_time': float
                }
        """
        start_time = datetime.now()
        
        # Determinar período del reporte
        if month is None or year is None:
            now = datetime.now()
            month = month or now.month
            year = year or now.year
        
        logger.info(f"📊 Generando reporte para {month}/{year}")
        
        try:
            # 1. Calcular resumen ejecutivo
            logger.info("   📈 Calculando resumen ejecutivo...")
            summary = self.create_executive_summary(data, month, year)
            
            # 2. Generar gráficos
            logger.info("   📊 Generando gráficos...")
            charts = self._generate_basic_charts(data, month, year)
            
            # 3. Calcular estadísticas
            logger.info("   🔢 Calculando estadísticas...")
            stats = self._calculate_statistics(data)
            
            # 4. Generar recomendaciones
            logger.info("   💡 Generando recomendaciones...")
            recommendations = self.generate_recommendations(data, summary, anomalies)
            
            # 5. Preparar datos para template
            template_data = {
                'report_month': self._get_month_name(month),
                'report_year': year,
                'generation_date': datetime.now().strftime('%d/%m/%Y %H:%M'),
                'report_id': f"RPT-{year}{month:02d}-{datetime.now().strftime('%H%M%S')}",
                'summary': summary,
                'charts': charts,
                'stats': stats,
                'predictions': self._process_predictions(predictions) if predictions else None,
                'anomalies': self._process_anomalies(anomalies) if anomalies else None,
                'recommendations': recommendations
            }
            
            # 6. Renderizar HTML
            logger.info("   🌐 Renderizando HTML...")
            html_content = self.render_html_report(template_data)
            
            # 7. Guardar HTML
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            html_filename = f"reporte_{year}-{month:02d}_{timestamp}.html"
            html_path = self.output_dir / html_filename
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"✅ Reporte HTML generado: {html_path}")
            
            # 8. Calcular tiempo de generación
            generation_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'html_path': str(html_path),
                'pdf_path': None,  # TODO: Implementar PDF en siguiente fase
                'charts': charts,
                'summary': summary,
                'status': 'success',
                'generation_time': generation_time
            }
            
            logger.info(f"🎉 Reporte completado en {generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando reporte: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'status': 'error',
                'error': str(e),
                'generation_time': (datetime.now() - start_time).total_seconds()
            }
    
    
    def create_executive_summary(
        self,
        data: pd.DataFrame,
        month: int,
        year: int
    ) -> Dict:
        """
        📊 Generar resumen ejecutivo con KPIs principales.
        
        Calcula:
        - Consumo total del período
        - Consumo promedio diario
        - Cambio porcentual vs mes anterior
        - Score de eficiencia
        - Total de anomalías
        
        Args:
            data: DataFrame con datos de consumo
            month: Mes del reporte
            year: Año del reporte
            
        Returns:
            Dict con KPIs calculados
        """
        # Filtrar datos del mes específico - Cast explícito para type safety
        idx = pd.DatetimeIndex(data.index)
        mask = (idx.month == month) & (idx.year == year)
        monthly_data = data[mask]
        
        if len(monthly_data) == 0:
            logger.warning(f"⚠️ No hay datos para {month}/{year}")
            # Usar todos los datos disponibles
            monthly_data = data
        
        # KPI 1: Consumo total (convertir de kW promedio a kWh)
        # Asumiendo datos por minuto: kW * (1/60) * num_registros
        consumption_kwh = monthly_data['Global_active_power'].sum() / 60
        
        # KPI 2: Consumo promedio diario
        daily_avg = monthly_data['Global_active_power'].mean()
        daily_max = monthly_data['Global_active_power'].max()
        daily_min = monthly_data['Global_active_power'].min()
        
        # KPI 3: Cambio porcentual vs mes anterior
        # (Simplificado por ahora - comparar con datos disponibles)
        change_pct = 0.0
        try:
            # Intentar obtener mes anterior
            prev_month = month - 1 if month > 1 else 12
            prev_year = year if month > 1 else year - 1
            
            # Cast explícito para type safety
            idx_full = pd.DatetimeIndex(data.index)
            prev_mask = (idx_full.month == prev_month) & (idx_full.year == prev_year)
            prev_data = data[prev_mask]
            
            if len(prev_data) > 0:
                prev_consumption = prev_data['Global_active_power'].sum() / 60
                change_pct = ((consumption_kwh - prev_consumption) / prev_consumption) * 100
        except:
            pass
        
        # KPI 4: Score de eficiencia (0-100)
        # Basado en consumo vs ideal (simplificado)
        mean_consumption = monthly_data['Global_active_power'].mean()
        median_consumption = monthly_data['Global_active_power'].median()
        
        # Score: mejor si está cerca de la mediana (uso equilibrado)
        variance_ratio = abs(mean_consumption - median_consumption) / mean_consumption
        efficiency_score = int(max(0, min(100, 100 - (variance_ratio * 200))))
        
        # KPI 5: Anomalías (placeholder - se actualiza si hay datos)
        total_anomalies = 0
        critical_anomalies = 0
        
        summary = {
            'total_consumption': float(consumption_kwh),
            'daily_avg': float(daily_avg),
            'daily_max': float(daily_max),
            'daily_min': float(daily_min),
            'change_pct': float(change_pct),
            'efficiency_score': efficiency_score,
            'total_anomalies': total_anomalies,
            'critical_anomalies': critical_anomalies,
            'period_days': len(monthly_data.resample('D').mean()),
            'total_records': len(monthly_data)
        }
        
        logger.info(f"   ✅ Resumen ejecutivo calculado")
        logger.info(f"      Consumo total: {consumption_kwh:.2f} kWh")
        logger.info(f"      Promedio diario: {daily_avg:.3f} kW")
        logger.info(f"      Cambio vs anterior: {change_pct:+.1f}%")
        
        return summary
    
    
    def _generate_basic_charts(
        self,
        data: pd.DataFrame,
        month: int,
        year: int
    ) -> Dict[str, str]:
        """
        📈 Generar gráficos básicos para el reporte.
        
        Args:
            data: DataFrame con datos de consumo
            month: Mes del reporte
            year: Año del reporte
            
        Returns:
            Dict con rutas de los gráficos generados
        """
        charts = {}
        
        # Filtrar datos del mes - Cast explícito para type safety
        idx = pd.DatetimeIndex(data.index)
        mask = (idx.month == month) & (idx.year == year)
        monthly_data = data[mask]
        
        if len(monthly_data) == 0:
            monthly_data = data  # Fallback a todos los datos
        
        # Gráfico 1: Consumo diario
        chart_path = self._plot_daily_consumption(monthly_data, month, year)
        charts['daily_consumption'] = chart_path
        
        logger.info(f"   ✅ Gráfico de consumo diario generado")
        
        return charts
    
    
    def _plot_daily_consumption(
        self,
        data: pd.DataFrame,
        month: int,
        year: int
    ) -> str:
        """
        Generar gráfico de consumo diario.
        
        Args:
            data: DataFrame con datos filtrados del mes
            month: Mes del reporte
            year: Año del reporte
            
        Returns:
            Ruta del gráfico generado
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Resample a diario
        daily = data['Global_active_power'].resample('D').mean()
        
        # Plot principal - Convertir a numpy para compatibilidad con matplotlib
        ax.plot(daily.index, daily.to_numpy(),
                linewidth=2.5, color='#667eea',
                marker='o', markersize=4,
                label='Consumo Diario')
        
        # Media móvil 7 días
        if len(daily) >= 7:
            ma7 = daily.rolling(window=7).mean()
            ax.plot(ma7.index, ma7.to_numpy(),
                    linewidth=2, linestyle='--',
                    color='#764ba2', alpha=0.7,
                    label='Media Móvil 7 días')
        
        # Línea de promedio
        mean_val = daily.mean()
        ax.axhline(y=mean_val, color='#95a5a6',
                   linestyle=':', linewidth=1.5,
                   label=f'Promedio: {mean_val:.3f} kW')
        
        # Marcar días con alto consumo (>P90)
        p90 = daily.quantile(0.90)
        high_days = daily[daily > p90]
        if len(high_days) > 0:
            ax.scatter(high_days.index, high_days.to_numpy(),
                       color='#e74c3c', s=100, marker='o',
                       label='Consumo Alto (>P90)', zorder=5)
        
        # Configuración
        ax.set_title(f'Consumo Energético Diario - {self._get_month_name(month)} {year}',
                     fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Fecha', fontsize=12, fontweight='600')
        ax.set_ylabel('Potencia (kW)', fontsize=12, fontweight='600')
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Rotar etiquetas del eje X
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Guardar
        filename = f"daily_consumption_{year}{month:02d}_{datetime.now().strftime('%H%M%S')}.png"
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        return str(filepath)
    
    
    def _calculate_statistics(self, data: pd.DataFrame) -> Dict:
        """
        Calcular estadísticas adicionales del período.
        
        Args:
            data: DataFrame con datos de consumo
            
        Returns:
            Dict con estadísticas calculadas
        """
        # Consumo por día
        daily = data['Global_active_power'].resample('D').sum() / 60  # kWh
        
        # Día con mayor y menor consumo
        highest_idx = daily.idxmax()
        lowest_idx = daily.idxmin()
        
        # Consumo por hora - Cast explícito para type safety
        idx = pd.DatetimeIndex(data.index)
        hourly = data.groupby(idx.hour)['Global_active_power'].mean()
        peak_hour = hourly.idxmax()
        valley_hour = hourly.idxmin()
        
        stats = {
            'highest_day': pd.Timestamp(highest_idx).strftime('%d/%m/%Y'),
            'highest_value': float(daily.max()),
            'lowest_day': pd.Timestamp(lowest_idx).strftime('%d/%m/%Y'),
            'lowest_value': float(daily.min()),
            'peak_hour': int(peak_hour),
            'valley_hour': int(valley_hour)
        }
        
        return stats
    
    
    def generate_recommendations(
        self,
        data: pd.DataFrame,
        summary: Dict,
        anomalies: Optional[Dict] = None
    ) -> List[Dict]:
        """
        💡 Generar recomendaciones personalizadas basadas en patrones.
        
        Args:
            data: DataFrame con datos de consumo
            summary: Dict con resumen ejecutivo
            anomalies: Dict con anomalías detectadas (opcional)
            
        Returns:
            Lista de recomendaciones con formato:
                [{'title': str, 'description': str, 'savings': str}, ...]
        """
        recommendations = []
        
        # Recomendación 1: Basada en cambio de consumo
        if summary['change_pct'] > 10:
            recommendations.append({
                'title': 'Reducir Consumo Excesivo',
                'description': f"El consumo aumentó {summary['change_pct']:.1f}% respecto al mes anterior. "
                              "Revisar equipos que puedan estar consumiendo más de lo normal, especialmente "
                              "durante horas pico (19:00-22:00 hrs).",
                'savings': 'Hasta 15% mensual'
            })
        
        # Recomendación 2: Basada en eficiencia
        if summary['efficiency_score'] < 70:
            recommendations.append({
                'title': 'Mejorar Eficiencia Energética',
                'description': f"Score de eficiencia actual: {summary['efficiency_score']}/100. "
                              "Considerar actualizar electrodomésticos antiguos por modelos de alta eficiencia "
                              "energética (categoría A+ o superior).",
                'savings': 'Hasta 20% mensual'
            })
        
        # Recomendación 3: Basada en patrones horarios - Cast explícito para type safety
        idx = pd.DatetimeIndex(data.index)
        hourly = data.groupby(idx.hour)['Global_active_power'].mean()
        night_consumption = hourly[(hourly.index >= 0) & (hourly.index <= 5)].mean()
        
        if night_consumption > hourly.mean() * 0.3:
            recommendations.append({
                'title': 'Reducir Consumo Nocturno',
                'description': "Se detectó consumo significativo durante horas de la madrugada (00:00-05:00). "
                              "Revisar equipos que puedan estar encendidos innecesariamente durante la noche "
                              "(calentadores de agua, luces exteriores, etc.).",
                'savings': 'Hasta 10% mensual'
            })
        
        # Recomendación por defecto si está bien
        if len(recommendations) == 0:
            recommendations.append({
                'title': 'Mantener Buenos Hábitos',
                'description': "El consumo está dentro de rangos óptimos. Continuar con los buenos hábitos "
                              "de eficiencia energética actuales.",
                'savings': None
            })
        
        logger.info(f"   ✅ {len(recommendations)} recomendaciones generadas")
        
        return recommendations
    
    
    def render_html_report(self, template_data: Dict) -> str:
        """
        🌐 Renderizar reporte HTML desde template Jinja2.
        
        Lee el archivo CSS y lo inyecta directamente en el HTML para
        que el reporte sea autocontenido y funcione en cualquier ubicación.
        
        Args:
            template_data: Dict con datos para el template
            
        Returns:
            String con HTML renderizado con CSS embebido
        """
        try:
            # Leer CSS y agregarlo a los datos del template
            css_path = self.template_dir / 'styles' / 'report_styles.css'
            
            if css_path.exists():
                with open(css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                template_data['inline_css'] = css_content
                logger.info(f"   📄 CSS cargado: {len(css_content)} caracteres")
            else:
                logger.warning(f"   ⚠️ CSS no encontrado en {css_path}, usando estilos por defecto")
                template_data['inline_css'] = "/* CSS no encontrado */"
            
            # Renderizar template
            template = self.jinja_env.get_template('monthly_report.html')
            html_content = template.render(**template_data)
            
            logger.info("   ✅ Template HTML renderizado con CSS embebido")
            
            return html_content
            
        except Exception as e:
            logger.error(f"   ❌ Error renderizando template: {e}")
            raise
    
    
    def export_to_pdf(
        self,
        html_path: str,
        output_path: Optional[str] = None,
        add_metadata: bool = True
    ) -> str:
        """
        📄 Convertir reporte HTML existente a PDF con xhtml2pdf.
        
        Convierte el reporte HTML generado a formato PDF optimizado para
        impresión, con estilos apropiados y metadatos opcionales.
        
        Args:
            html_path: Ruta al archivo HTML generado
            output_path: Ruta de salida del PDF (None = automático)
            add_metadata: Si añadir metadatos al PDF (no implementado en xhtml2pdf)
            
        Returns:
            Ruta del archivo PDF generado
            
        Raises:
            ImportError: Si xhtml2pdf no está instalado
            FileNotFoundError: Si el HTML no existe
            
        Example:
            >>> generator = ReportGenerator()
            >>> html_path = generator.generate_monthly_report(df, month=6, year=2007)['html_path']
            >>> pdf_path = generator.export_to_pdf(html_path)
            >>> print(f"PDF generado: {pdf_path}")
        """
        if not PDF_AVAILABLE:
            raise ImportError(
                "xhtml2pdf no está instalado. "
                "Instala con: pip install xhtml2pdf"
            )
        
        try:
            logger.info(f"📄 Convirtiendo HTML a PDF...")
            logger.info(f"   Fuente: {html_path}")
            
            # Determinar ruta de salida
            if output_path is None:
                output_path = str(html_path).replace('.html', '.pdf')
            
            # Verificar que HTML existe
            html_file = Path(html_path)
            if not html_file.exists():
                raise FileNotFoundError(f"❌ HTML no encontrado: {html_path}")
            
            # Leer HTML
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # CSS adicional optimizado para PDF en xhtml2pdf
            pdf_css = """
            <style type="text/css">
                @page {
                    size: a4 portrait;
                    margin: 2cm 1.5cm;
                    @frame footer {
                        -pdf-frame-content: footerContent;
                        bottom: 1cm;
                        margin-left: 1.5cm;
                        margin-right: 1.5cm;
                        height: 1cm;
                    }
                }
                
                /* Evitar saltos de página inapropiados */
                .kpi-card, .chart-container, .recommendations-list li {
                    page-break-inside: avoid;
                }
                
                section {
                    page-break-inside: avoid;
                    page-break-after: auto;
                }
                
                /* Ajustar gráficos para impresión */
                .chart-container img {
                    max-width: 100%;
                    height: auto;
                    page-break-inside: avoid;
                }
                
                /* Optimizar fuentes para PDF */
                body {
                    font-size: 11pt;
                    line-height: 1.5;
                }
                
                h2 {
                    font-size: 18pt;
                    page-break-after: avoid;
                    color: #667eea;
                }
                
                h3 {
                    font-size: 14pt;
                    page-break-after: avoid;
                }
            </style>
            """
            
            # Inyectar CSS adicional antes del cierre del </head>
            if '</head>' in html_content:
                html_content = html_content.replace('</head>', f'{pdf_css}</head>')
            
            # Generar PDF con xhtml2pdf
            with open(output_path, 'w+b') as pdf_file:
                pisa_status = pisa.CreatePDF(
                    html_content.encode('utf-8'),
                    dest=pdf_file,
                    encoding='utf-8'
                )
            
            # Obtener tamaño del archivo
            pdf_size = Path(output_path).stat().st_size / 1024  # KB
            
            logger.info(f"   ✅ PDF generado: {output_path}")
            logger.info(f"   📊 Tamaño: {pdf_size:.1f} KB")
            
            return output_path
            
        except Exception as e:
            logger.error(f"   ❌ Error generando PDF: {e}")
            raise
    
    
    def generate_monthly_report_with_pdf(
        self,
        data: pd.DataFrame,
        month: int,
        year: int,
        format: str = 'both',
        predictions: Optional[Dict] = None,
        anomalies: Optional[Dict] = None
    ) -> Dict:
        """
        🚀 Generar reporte mensual en formato HTML y/o PDF.
        
        Esta función extiende generate_monthly_report() para soportar
        exportación directa a PDF además de HTML.
        
        Args:
            data: DataFrame con datos de consumo
            month: Mes del reporte (1-12)
            year: Año del reporte (ej: 2007, 2025)
            format: Formato de salida:
                - 'html': Solo HTML
                - 'pdf': Solo PDF (genera HTML temporal)
                - 'both': HTML + PDF (recomendado)
            predictions: Opcional - Dict con predicciones
            anomalies: Opcional - Dict con anomalías
            
        Returns:
            Diccionario con:
                - html_path: Ruta al HTML (si format='html' o 'both')
                - pdf_path: Ruta al PDF (si format='pdf' o 'both')
                - consumption_kwh: Consumo mensual total
                - change_percent: Cambio vs mes anterior
                - efficiency_score: Score de eficiencia
                - generation_time: Tiempo de generación
                
        Example:
            >>> import pandas as pd
            >>> df = pd.read_csv('data/Dataset_clean_test.csv', 
            ...                  parse_dates=['Datetime'], index_col='Datetime')
            >>> generator = ReportGenerator()
            
            >>> # Generar ambos formatos
            >>> result = generator.generate_monthly_report_with_pdf(
            ...     df, 6, 2007, format='both'
            ... )
            >>> print(f"HTML: {result['html_path']}")
            >>> print(f"PDF: {result['pdf_path']}")
            
            >>> # Solo PDF
            >>> result = generator.generate_monthly_report_with_pdf(
            ...     df, 6, 2007, format='pdf'
            ... )
            >>> print(f"PDF: {result['pdf_path']}")
        """
        start_time = datetime.now()
        
        # Validar formato
        valid_formats = ['html', 'pdf', 'both']
        if format not in valid_formats:
            raise ValueError(f"Formato inválido: {format}. Use: {valid_formats}")
        
        logger.info(f"📊 Generando reporte en formato: {format}")
        
        # Generar HTML primero (siempre necesario)
        html_result = self.generate_monthly_report(
            data=data,
            predictions=predictions,
            anomalies=anomalies,
            month=month,
            year=year
        )
        
        result = {
            'html_path': html_result['html_path'] if format != 'pdf' else None,
            'pdf_path': None,
            'consumption_kwh': html_result.get('summary', {}).get('consumption_kwh', 0),
            'change_percent': html_result.get('summary', {}).get('change_pct', 0),
            'efficiency_score': html_result.get('summary', {}).get('efficiency_score', 0),
            'charts': html_result.get('charts', {}),
            'generation_time': 0
        }
        
        # Generar PDF si se solicita
        if format in ['pdf', 'both']:
            try:
                pdf_path = self.export_to_pdf(html_result['html_path'])
                result['pdf_path'] = pdf_path
                
                # Si solo se quiere PDF, eliminar HTML temporal
                if format == 'pdf':
                    html_file = Path(html_result['html_path'])
                    if html_file.exists():
                        html_file.unlink()
                        logger.info(f"🗑️  HTML temporal eliminado")
                        result['html_path'] = None
                        
            except Exception as e:
                logger.error(f"❌ Error generando PDF: {e}")
                # No fallar si solo HTML es posible
                if format == 'pdf':
                    raise
                logger.warning(f"⚠️  Continuando solo con HTML")
        
        # Calcular tiempo total
        end_time = datetime.now()
        result['generation_time'] = (end_time - start_time).total_seconds()
        
        logger.info(f"🎉 Reporte completado en {result['generation_time']:.2f}s")
        
        return result
    
    
    def _get_month_name(self, month: int) -> str:
        """Obtener nombre del mes en español."""
        months = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }
        return months.get(month, f'Mes {month}')
    
    
    def _process_predictions(self, predictions: Dict) -> Dict:
        """Procesar datos de predicciones para el template."""
        # Simplificado por ahora
        return {
            'total_7days': predictions.get('statistics', {}).get('total_consumption', 0),
            'daily_avg': predictions.get('statistics', {}).get('mean_consumption', 0),
            'estimated_bill': predictions.get('statistics', {}).get('total_consumption', 0) * 0.15,  # $0.15/kWh
            'confidence': 85  # Placeholder
        }
    
    
    def _process_anomalies(self, anomalies: Dict) -> Dict:
        """Procesar datos de anomalías para el template."""
        # Simplificado por ahora
        top_critical = []
        
        if 'alerts' in anomalies:
            for alert in anomalies['alerts'][:10]:
                if alert.get('severity') == 'critical':
                    top_critical.append({
                        'timestamp': alert.get('timestamp'),
                        'type': alert.get('type', ''),
                        'consumption': alert.get('value', 0),
                        'severity': alert.get('severity', ''),
                        'description': alert.get('description', '')
                    })
        
        return {
            'top_critical': top_critical
        }


# ============================================================================
# FUNCIÓN DE CONVENIENCIA
# ============================================================================

def generate_quick_report(
    data_path: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
    format: str = 'html'
) -> Dict:
    """
    ⚡ Generación rápida de reporte para scripts.
    
    Args:
        data_path: Ruta al archivo CSV con datos limpios
        month: Mes del reporte (default: mes actual)
        year: Año del reporte (default: año actual)
        format: Formato de salida: 'html', 'pdf', o 'both'
        
    Returns:
        Dict con resultado de la generación:
            - html_path: Ruta al HTML (si format='html' o 'both')
            - pdf_path: Ruta al PDF (si format='pdf' o 'both')
            - consumption_kwh: Consumo mensual
            - change_percent: Cambio vs mes anterior
            - efficiency_score: Score de eficiencia
            - generation_time: Tiempo total
        
    Example:
        >>> from src.reporting import generate_quick_report
        
        >>> # Solo HTML (default)
        >>> report = generate_quick_report('data/Dataset_clean_test.csv')
        >>> print(f"HTML: {report['html_path']}")
        
        >>> # HTML + PDF
        >>> report = generate_quick_report(
        ...     'data/Dataset_clean_test.csv',
        ...     month=6,
        ...     year=2007,
        ...     format='both'
        ... )
        >>> print(f"HTML: {report['html_path']}")
        >>> print(f"PDF: {report['pdf_path']}")
        
        >>> # Solo PDF
        >>> report = generate_quick_report(
        ...     'data/Dataset_clean_test.csv',
        ...     format='pdf'
        ... )
        >>> print(f"PDF: {report['pdf_path']}")
    """
    # Cargar datos
    logger.info(f"📂 Cargando datos desde {data_path}")
    df = pd.read_csv(data_path, parse_dates=['Datetime'], index_col='Datetime')
    
    # Generar reporte
    generator = ReportGenerator()
    
    if format == 'html':
        # Solo HTML (comportamiento original)
        report = generator.generate_monthly_report(
            data=df,
            predictions=None,
            anomalies=None,
            month=month,
            year=year
        )
    else:
        # HTML y/o PDF
        report = generator.generate_monthly_report_with_pdf(
            data=df,
            month=month or datetime.now().month,
            year=year or datetime.now().year,
            format=format,
            predictions=None,
            anomalies=None
        )
    
    return report


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplo de uso del ReportGenerator.
    """
    print("=" * 80)
    print("📋 DomusAI - Generador de Reportes")
    print("=" * 80)
    
    # Generar reporte rápido
    print("\n📊 Generando reporte de prueba...")
    
    result = generate_quick_report(
        data_path='data/Dataset_clean_test.csv',
        month=6,
        year=2007
    )
    
    if result['status'] == 'success':
        print(f"\n✅ Reporte generado exitosamente!")
        print(f"   📄 HTML: {result['html_path']}")
        print(f"   ⏱️  Tiempo: {result['generation_time']:.2f}s")
    else:
        print(f"\n❌ Error: {result.get('error')}")
    
    print("\n" + "=" * 80)
