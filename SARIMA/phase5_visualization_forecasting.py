from __future__ import annotations

import pickle
from pathlib import Path
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
SARIMA_DIR = ROOT / "SARIMA"
DATA_DIR = ROOT / "data"

# Files
HYBRID_FORECASTS = SARIMA_DIR / "hybrid_forecasts_all.csv"
METRICS_ALL = SARIMA_DIR / "metrics_all_series.csv"
METRICS_SUM = SARIMA_DIR / "metrics_summary.csv"
XGB_MODEL = SARIMA_DIR / "xgb_residual_model.json"
FEATURE_COLS = SARIMA_DIR / "xgb_feature_columns.txt"
ENCODERS = SARIMA_DIR / "label_encoders.pkl"
WEEKLY = DATA_DIR / "weekly_demand_categorie_region.csv"
SARIMA_MODELS_DIR = SARIMA_DIR / "models"

# Outputs
OUT_FORECAST_PLOTS = SARIMA_DIR / "forecast_plots_top6.png"
OUT_METRICS_COMP = SARIMA_DIR / "metrics_comparison_by_region.png"
OUT_HEATMAP = SARIMA_DIR / "improvement_heatmap.png"
OUT_RESID_CORR = SARIMA_DIR / "residual_correction_fit.png"
OUT_FUTURE = SARIMA_DIR / "future_forecast_Q1_2026.csv"

RAMADAN_RANGES = [("2024-03-11", "2024-04-09"), ("2025-03-01", "2025-03-29"), ("2026-02-18", "2026-03-19")]
EID_RANGES = []

def load_artifacts():
    hybrid = pd.read_csv(HYBRID_FORECASTS, parse_dates=["date"]) if HYBRID_FORECASTS.exists() else None
    metrics = pd.read_csv(METRICS_ALL) if METRICS_ALL.exists() else None
    feat_cols = [l.strip() for l in FEATURE_COLS.read_text(encoding="utf-8").splitlines() if l.strip()]
    booster = xgb.Booster(); booster.load_model(str(XGB_MODEL))
    with open(ENCODERS, "rb") as f:
        enc = pickle.load(f)
    weekly = pd.read_csv(WEEKLY, parse_dates=[0])
    # normalize column name
    weekly.columns = [c if 'date' in c.lower() or 'date' in c else c for c in weekly.columns]
    # ensure standard names
    # find date column
    date_col = [c for c in weekly.columns if 'date' in c.lower() or 'expedi' in c.lower()][0]
    weekly = weekly.rename(columns={date_col: 'date'})
    return hybrid, metrics, feat_cols, booster, enc, weekly


def plot_forecasts_top6(hybrid, weekly):
    # top6 by total demand
    total = weekly.groupby(['Categorie', 'region'], sort=False)['demand'].sum().reset_index()
    total['key'] = total['Categorie'] + '||' + total['region']
    top6 = total.sort_values('demand', ascending=False).head(6)
    keys = [(r.split('||')[0], r.split('||')[1]) for r in top6['Categorie'] + '||' + top6['region']]

    fig, axes = plt.subplots(2,3,figsize=(18,10))
    axes = axes.flatten()
    for ax, (cat, reg) in zip(axes, keys):
        ser = weekly[(weekly['Categorie']==cat)&(weekly['region']==reg)].sort_values('date')
        ax.plot(ser['date'], ser['demand'], label='Actual', color='black')
        # overlay SARIMA and Hybrid for val+test
        hmask = (hybrid['Categorie']==cat)&(hybrid['region']==reg)
        if hmask.any():
            h = hybrid[hmask].sort_values('date')
            # SARIMA forecast column in hybrid file is 'sarima_forecast_val'
            if 'sarima_forecast_val' in h.columns:
                ax.plot(h['date'], h['sarima_forecast_val'], label='SARIMA (val+test)', linestyle='--')
            elif 'sarima_forecast' in h.columns:
                ax.plot(h['date'], h['sarima_forecast'], label='SARIMA (val+test)', linestyle='--')
            ax.plot(h['date'], h['hybrid_forecast'], label='Hybrid (val+test)', linestyle=':')
            # determine split boundaries
            val_start = h[h['split']=='validation']['date'].min()
            test_start = h[h['split']=='test']['date'].min()
            if pd.notna(val_start):
                ax.axvspan(ser['date'].min(), val_start - pd.Timedelta(days=1), color='#e6f2ff', alpha=0.3)
            if pd.notna(val_start) and pd.notna(test_start):
                ax.axvspan(val_start, test_start - pd.Timedelta(days=1), color='#fff4e6', alpha=0.3)
            if pd.notna(test_start):
                ax.axvspan(test_start, ser['date'].max(), color='#f0ffe6', alpha=0.2)
        # Ramadan bands
        for rs, re in RAMADAN_RANGES:
            ax.axvspan(pd.to_datetime(rs), pd.to_datetime(re), color='red', alpha=0.08)
        ax.set_title(f"{cat} — {reg}")
        ax.legend()
    plt.tight_layout()
    fig.savefig(OUT_FORECAST_PLOTS, dpi=200)
    plt.close(fig)


def metrics_comparison_bar(metrics):
    # filter test split and metrics of interest
    df = metrics[metrics['split']=='test'].copy()
    regions = ['NORTH','WEST','EAST','SOUTH']
    metrics_list = ['MAE','RMSE','SMAPE','MASE']
    fig, axes = plt.subplots(2,2,figsize=(14,10))
    axes = axes.flatten()
    for ax, metric in zip(axes, metrics_list):
        pivot = df.groupby(['region','model'])[metric].mean().unstack().reindex(regions)
        pivot.plot(kind='bar', ax=ax)
        ax.set_title(metric)
        ax.set_xlabel('Region')
        ax.legend()
    plt.tight_layout()
    fig.savefig(OUT_METRICS_COMP, dpi=200)
    plt.close(fig)


def improvement_heatmap(metrics):
    # compute RMSE improvement % per category x region on test
    df = metrics[metrics['split']=='test']
    pivot_sarima = df[df['model']=='SARIMA'].pivot(index='Categorie', columns='region', values='RMSE')
    pivot_hybrid = df[df['model']=='Hybrid'].pivot(index='Categorie', columns='region', values='RMSE')
    # align
    cats = sorted(set(pivot_sarima.index) | set(pivot_hybrid.index))
    regs = ['NORTH','WEST','EAST','SOUTH']
    sar = pivot_sarima.reindex(index=cats, columns=regs)
    hyb = pivot_hybrid.reindex(index=cats, columns=regs)
    improvement = (sar - hyb) / sar * 100
    plt.figure(figsize=(12,10))
    import seaborn as sns
    sns.heatmap(improvement, cmap='RdYlGn', center=0, linewidths=0.5)
    plt.title('RMSE improvement % (Hybrid vs SARIMA) — test')
    plt.tight_layout()
    plt.savefig(OUT_HEATMAP, dpi=200)
    plt.close()


def residual_correction_plot(hybrid):
    # pick top series per region by total demand in hybrid (or weekly)
    regs = ['NORTH','EAST','SOUTH','WEST']
    picks = []
    for r in regs:
        sub = hybrid[hybrid['region']==r]
        if sub.empty:
            continue
        actual_col = 'actual_demand' if 'actual_demand' in sub.columns else 'actual'
        grp = sub.groupby('Categorie')[actual_col].sum().sort_values(ascending=False)
        if grp.empty:
            continue
        cat = grp.index[0]
        picks.append((cat,r))
    fig, axes = plt.subplots(2,2,figsize=(12,8))
    axes = axes.flatten()
    for ax, (cat, r) in zip(axes, picks):
        sub = hybrid[(hybrid['Categorie']==cat)&(hybrid['region']==r)].sort_values('date')
        if sub.empty:
            continue
        # actual residual = actual - sarima_forecast
        # hybrid file uses 'actual' and 'sarima_forecast_val'
        if 'actual_demand' in sub.columns:
            sub['actual_residual'] = sub['actual_demand'] - (sub['sarima_forecast_val'] if 'sarima_forecast_val' in sub.columns else sub.get('sarima_forecast'))
        else:
            sub['actual_residual'] = sub['actual'] - (sub['sarima_forecast_val'] if 'sarima_forecast_val' in sub.columns else sub.get('sarima_forecast'))
        ax.plot(sub['date'], sub['actual_residual'], label='Actual residual', color='black')
        ax.plot(sub['date'], sub['xgb_correction'], label='XGB predicted correction', color='green')
        ax.set_title(f"{cat} — {r}")
        ax.legend()
    plt.tight_layout()
    plt.savefig(OUT_RESID_CORR, dpi=200)
    plt.close()


def forecast_future(booster, feat_cols, encoders, weekly):
    # For each series, load SARIMA model and predict 12 weeks
    rows = []
    # prepare maps
    demand_map_region = weekly.groupby('region')['demand'].mean().to_dict()
    demand_map_cat = weekly.groupby('Categorie')['demand'].mean().to_dict()

    for model_file in SARIMA_MODELS_DIR.glob('sarima_*.pkl'):
        name = model_file.stem.replace('sarima_','')
        # name may contain category and region
        parts = name.rsplit('_',1)
        if len(parts)!=2:
            continue
        cat_raw, reg_raw = parts[0], parts[1]
        # revert normalization if needed
        try:
            with open(model_file,'rb') as f:
                m = pickle.load(f)
        except Exception:
            continue
        # determine last known series
        ser = weekly[(weekly['Categorie'].str.replace('\\s+',' ',regex=True)==cat_raw) & (weekly['region']==reg_raw)].sort_values('date')
        if ser.empty:
            # try variants
            ser = weekly[(weekly['Categorie'].str.contains(parts[0], case=False, na=False)) & (weekly['region']==reg_raw)].sort_values('date')
            if ser.empty:
                continue
        last_date = ser['date'].max()
        future_dates = pd.date_range(last_date + pd.Timedelta(days=7), periods=12, freq='W-MON')
        # SARIMA forecast
        try:
            sarima_fore = m.predict(n_periods=12)
        except Exception:
            try:
                sarima_fore = m.forecast(12)
            except Exception:
                sarima_fore = [np.nan]*12
        sarima_fore = np.array(sarima_fore).astype(float)
        # build features per future week
        history = ser.set_index('date')['demand'].asfreq('W-MON').fillna(0)
        for i, dt in enumerate(future_dates):
            feat = {}
            feat['week_of_year'] = int(dt.isocalendar()[1])
            feat['month'] = dt.month
            feat['quarter'] = (dt.quarter)
            feat['is_ramadan'] = int(any(pd.to_datetime(r[0])<=dt<=pd.to_datetime(r[1]) for r in RAMADAN_RANGES))
            feat['is_summer'] = int(dt.month in (7,8))
            feat['is_eid'] = 0
            # encodings
            feat['categorie_encoded'] = encoders['Categorie'].transform([cat_raw])[0] if 'Categorie' in encoders else 0
            feat['region_encoded'] = encoders['region'].transform([reg_raw])[0] if 'region' in encoders else 0
            feat['categorie_region_id'] = 0
            feat['demand_per_region'] = demand_map_region.get(reg_raw, np.nan)
            feat['demand_per_categorie'] = demand_map_cat.get(cat_raw, np.nan)
            # lags
            for lag in [1,2,3,4,8,12,26,52]:
                d = dt - pd.Timedelta(weeks=lag)
                val = history.reindex([d]).fillna(0).values[0] if not history.empty else 0
                feat[f'lag_{lag}'] = val
            for window in [4,12,26]:
                vals = [history.reindex([dt - pd.Timedelta(weeks=w)]).fillna(0).values[0] for w in range(1,window+1)]
                feat[f'rolling_mean_{window}'] = np.mean(vals)
                if window in (4,12):
                    feat[f'rolling_std_{window}'] = np.std(vals)
            feat['sarima_forecast_val'] = sarima_fore[i]
            # ensure order
            row = [feat.get(c, 0.0) for c in feat_cols]
            dmat = xgb.DMatrix(pd.DataFrame([row], columns=feat_cols), feature_names=feat_cols)
            try:
                xgb_corr = float(booster.predict(dmat)[0])
            except Exception:
                xgb_corr = np.nan
            hybrid = float(sarima_fore[i]) + xgb_corr
            rows.append({'date': dt, 'Categorie': cat_raw, 'region': reg_raw, 'sarima_forecast': float(sarima_fore[i]), 'xgb_correction': xgb_corr, 'hybrid_forecast': hybrid})
    df_out = pd.DataFrame(rows)
    df_out.to_csv(OUT_FUTURE, index=False)
    return df_out


def print_report(metrics):
    # aggregate test results
    test = metrics[metrics['split']=='test']
    sar = test[test['model']=='SARIMA'][['MAE','RMSE','SMAPE','MASE','R2']].mean()
    hyp = test[test['model']=='Hybrid'][['MAE','RMSE','SMAPE','MASE','R2']].mean()
    improvement = (sar - hyp) / sar * 100
    improved_pct = (test.pivot_table(index=['Categorie','region'], columns='model', values='RMSE').apply(lambda row: row['SARIMA']>row['Hybrid'], axis=1).mean()*100)
    best_region = test[test['model']=='Hybrid'].groupby('region')['RMSE'].mean().sort_values().index[0]
    best_cat_row = (test[test['model']=='Hybrid'].groupby('Categorie')['RMSE'].mean() - test[test['model']=='SARIMA'].groupby('Categorie')['RMSE'].mean()).sort_values().idxmax()

    print('\n' + '━'*60)
    print('  HYBRID SARIMA+XGBoost — FINAL RESULTS')
    print('━'*60)
    print('Dataset:    220,000 orders | 2024–2025 | Algeria')
    print('Series:     {} active (Categorie × region) tuples'.format(test[['Categorie','region']].drop_duplicates().shape[0]))
    print('Frequency:  Weekly\n')
    print('TEST SET RESULTS:')
    print('            MAE    RMSE   SMAPE   MASE    R2')
    print('SARIMA   {:5.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}'.format(sar['MAE'], sar['RMSE'], sar['SMAPE'], sar['MASE'], sar['R2']))
    print('Hybrid   {:5.3f} {:6.3f} {:6.3f} {:6.3f} {:6.3f}'.format(hyp['MAE'], hyp['RMSE'], hyp['SMAPE'], hyp['MASE'], hyp['R2']))
    print('Improvement {:5.2f}% {:6.2f}% {:6.2f}% {:6.2f}%'.format(improvement['MAE'], improvement['RMSE'], improvement['SMAPE'], improvement['MASE']))
    print(f'BEST REGION: {best_region}')
    print(f'BEST CATEGORY: {best_cat_row}')
    print(f'% series improved by Hybrid: {improved_pct:.2f}%')
    print(f'Q1 2026 Forecast: saved to {OUT_FUTURE}')
    print('━'*60)


def main():
    hybrid, metrics, feat_cols, booster, enc, weekly = load_artifacts()
    print('Artifacts loaded')
    # plots
    plot_forecasts_top6(hybrid, weekly)
    metrics_comparison_bar(metrics)
    improvement_heatmap(metrics)
    residual_correction_plot(hybrid)
    # future forecasts
    future = forecast_future(booster, feat_cols, enc, weekly)
    print_report(metrics)

if __name__=='__main__':
    main()
