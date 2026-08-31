'use client';
/* oxlint-disable typescript/no-deprecated */

import { useState, type CSSProperties } from 'react';
import Image from 'next/image';
import {
  AlertTriangle,
  BarChart3,
  Boxes,
  BrainCircuit,
  CheckCircle2,
  Info,
  MessageCircleMore,
  PackageSearch,
  Sparkles,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  Legend,
  Line,
  LineChart,
  Label,
  ReferenceLine,
  XAxis,
  YAxis,
} from 'recharts';

import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';

type View = 'Product Landscape' | 'Customer Voice Lab';

const palette = ['#FF4D78', '#FFC43D', '#22C983', '#8B5CF6', '#FF704D'];
const productScale = ['#FF704D', '#FF8261', '#FF9677', '#FFAB90', '#FFC0AA', '#FFD6C7'];

const priceTiers = [
  { tier: 'Budget', listings: 64, color: productScale[4] },
  { tier: 'Mass market', listings: 73, color: productScale[3] },
  { tier: 'Premium', listings: 5, color: productScale[2] },
  { tier: 'High-end', listings: 8, color: productScale[0] },
];

const formats = [
  { format: 'Figurine', listings: 71 },
  { format: 'DIY kits', listings: 45 },
  { format: 'Other', listings: 12 },
  { format: 'Plush charms', listings: 10 },
  { format: 'Magnet', listings: 8 },
  { format: 'Gift sets', listings: 4 },
];

const segments = [
  { name: 'Official museum DIY kits', description: 'Official-store excavation and educational kits', count: 26, price: 74, official: 96, sales: 31, accent: palette[0] },
  { name: 'Mainstream museum gift range', description: 'Broad mix of mid-priced museum souvenirs', count: 62, price: 51, official: 85, sales: 45, accent: palette[1] },
  { name: 'Low-price marketplace DIY kits', description: 'Budget excavation kits, mostly outside official stores', count: 20, price: 16, official: 5, sales: 60, accent: palette[4] },
  { name: 'Higher-price official figurines', description: 'Official-store display collectibles at higher prices', count: 18, price: 69, official: 94, sales: 33, accent: palette[2] },
  { name: 'Character collectibles with sales data', description: 'Character-led items with complete displayed-sales fields', count: 24, price: 49, official: 79, sales: 100, accent: palette[3] },
];

const sentiment = [
  { label: 'Negative', share: 18.8, color: '#FF4D78' },
  { label: 'Neutral / Mixed', share: 8.4, color: '#FFC43D' },
  { label: 'Positive', share: 72.8, color: '#22C983' },
];

const aspects = [
  { aspect: 'Packaging', support: 15, f1: 1.0 },
  { aspect: 'Logistics', support: 17, f1: 0.97 },
  { aspect: 'Product Design', support: 67, f1: 0.72 },
  { aspect: 'Quality', support: 48, f1: 0.7 },
  { aspect: 'Price & Value', support: 26, f1: 0.51 },
  { aspect: 'Gifting & Education', support: 40, f1: 0.47 },
  { aspect: 'Blind-box Outcome', support: 6, f1: 0.18 },
];

const kEvaluation = [
  { k: 2, silhouette: 0.217, stability: 0.913 },
  { k: 3, silhouette: 0.253, stability: 0.956 },
  { k: 4, silhouette: 0.26, stability: 0.831 },
  { k: 5, silhouette: 0.283, stability: 0.966 },
  { k: 6, silhouette: 0.269, stability: 0.87 },
];

const ldaEvaluation = [
  { topics: 2, perplexity: 954, diversity: 0.9 },
  { topics: 3, perplexity: 1584, diversity: 0.9 },
  { topics: 4, perplexity: 2447, diversity: 0.825 },
  { topics: 5, perplexity: 3697, diversity: 0.68 },
  { topics: 6, perplexity: 5813, diversity: 0.617 },
];

const cardClass =
  'data-card rounded-[1.4rem] border border-[#171A2B]/8 bg-white shadow-[0_8px_28px_rgb(29_36_61/6%)]';

function SectionTitle({ eyebrow, title, copy, tone }: { eyebrow: string; title: string; copy?: string; tone?: string }) {
  return (
    <div className="section-heading text-left">
      <p className="text-xs font-bold uppercase tracking-[0.14em]" style={{ color: tone ?? 'var(--dashboard-accent, #e85f8c)' }}>{eyebrow}</p>
      <h2 className="mt-2 text-xl font-semibold tracking-tight sm:text-2xl">{title}</h2>
      {copy ? <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{copy}</p> : null}
    </div>
  );
}

function MetricCards() {
  const metrics = [
    { icon: Boxes, label: 'Product listings', value: '150', note: '5 public index pages', tone: 'bg-[#fff0f5]', accent: '#f06d9a' },
    { icon: BarChart3, label: 'Median price', value: 'CNY 59', note: '137 products ≤ CNY 100', tone: 'bg-[#fff7d8]', accent: '#f6c64e' },
    { icon: PackageSearch, label: 'Product formats', value: '6', note: 'Figurines and DIY lead', tone: 'bg-[#edf4ff]', accent: '#3A86FF' },
    { icon: Sparkles, label: 'Exploratory segments', value: '5', note: 'Minimum cluster size: 18', tone: 'bg-[#fff0f7]', accent: '#ff86bb' },
  ];
  return (
    <section aria-label="Key metrics" className="metric-ribbon">
      {metrics.map((item) => (
        <article key={item.label} className="metric-compact" style={{ '--metric-accent': item.accent } as CSSProperties}>
          <div className={`flex size-9 shrink-0 items-center justify-center rounded-xl ${item.tone}`}><item.icon className="size-4.5 shrink-0" /></div>
          <div className="min-w-0">
            <p className="whitespace-nowrap text-[10px] font-bold uppercase tracking-[0.1em] text-muted-foreground">{item.label}</p>
            <p className="mt-0.5 text-2xl font-bold tracking-tight">{item.value}</p>
            <p className="mt-0.5 text-[11px] text-muted-foreground">{item.note}</p>
          </div>
        </article>
      ))}
    </section>
  );
}

function SegmentMatrix() {
  return (
    <div className="segment-matrix-wrap">
      <section className="segment-matrix" aria-label="Five exploratory product segment profiles">
        <div className="segment-matrix-head"><span>Commercial profile</span><span>Listings</span><span>Median price</span><span>Official share</span><span>Sales coverage</span></div>
        {segments.map((segment) => (
          <div className="segment-matrix-row" key={segment.name}>
            <div className="segment-name"><span style={{ background: segment.accent }} /><div><strong>{segment.name}</strong><small>{segment.description}</small></div></div>
            <div className="segment-value" data-label="Listings"><strong>{segment.count}</strong><div><i style={{ width: `${segment.count / 62 * 100}%`, background: segment.accent }} /></div></div>
            <div className="segment-value" data-label="Median price"><strong>CNY {segment.price}</strong><div><i style={{ width: `${segment.price / 80 * 100}%`, background: segment.accent }} /></div></div>
            <div className="segment-value" data-label="Official share"><strong>{segment.official}%</strong><div><i style={{ width: `${segment.official}%`, background: segment.accent }} /></div></div>
            <div className="segment-value" data-label="Sales coverage"><strong>{segment.sales}%</strong><div><i style={{ width: `${segment.sales}%`, background: segment.accent }} /></div></div>
          </div>
        ))}
      </section>
      <p className="segment-note">Cluster names are analyst interpretations. Sales coverage measures field availability, not demand.</p>
    </div>
  );
}

function Overview() {
  return (
    <div className="space-y-4">
      <MetricCards />
      <section className="grid gap-4 xl:grid-cols-[0.82fr_1.18fr]">
        <article className={`${cardClass} p-5 sm:p-7`}>
          <SectionTitle eyebrow="01 · Price map" title="Where does the market compete on price?" copy="Most of the assortment is accessible rather than premium: 137 of 150 listings are priced at CNY 100 or below." />
          <ChartContainer config={{ listings: { label: 'Listings', color: palette[2] } }} className="mt-4 h-[250px] w-full aspect-auto">
            <BarChart data={priceTiers} layout="vertical" margin={{ top: 6, right: 28, left: 8, bottom: 0 }}>
              <CartesianGrid horizontal={false} /><XAxis type="number" tickLine={false} axisLine={false} /><YAxis dataKey="tier" type="category" width={82} tickLine={false} axisLine={false} />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar dataKey="listings" barSize={18} radius={[0, 9, 9, 0]}>{priceTiers.map((row) => <Cell key={row.tier} fill={row.color} />)}<LabelList dataKey="listings" position="right" className="fill-[#4f566d] text-[11px] font-bold" /></Bar>
            </BarChart>
          </ChartContainer>
        </article>
        <article className={`${cardClass} p-5 sm:p-7`}>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <SectionTitle eyebrow="02 · Product groups" title="What kinds of products appear together?" copy="Five exploratory groups summarize products with similar prices, formats, store signals, and sales-field coverage." />
            <span className="w-fit rounded-full bg-[#edf4ff] px-3 py-1.5 text-xs font-semibold text-[#185fc7]">Exploratory, not authenticity labels</span>
          </div>
          <SegmentMatrix />
        </article>
      </section>
      <section className="insight-strip">
        {[
          { title: 'Entry price drives breadth', copy: '137 of 150 listings sit at CNY 100 or below.', color: '#ef6b8f' },
          { title: 'Experience separates demand', copy: 'Collect/display and discover/build are two distinct shopping missions.', color: '#e3ad27' },
          { title: 'Premium remains a test', copy: 'Only 13 listings sit above the mass market; validate before scaling.', color: '#3A86FF' },
        ].map((item) => <article key={item.title} style={{ '--insight': item.color } as CSSProperties}><h3>{item.title}</h3><p>{item.copy}</p></article>)}
      </section>
    </div>
  );
}

function Products() {
  return (
    <div className="product-story-grid grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
      <article className={`${cardClass} p-5 sm:p-7`}>
        <SectionTitle eyebrow="03 · Format mix" title="What experience does each product format offer?" copy="Figurines are designed for collecting and display. DIY excavation kits add participation, education, and gifting." />
        <ChartContainer config={{ listings: { label: 'Listings', color: palette[2] } }} className="mt-5 h-[300px] w-full aspect-auto">
          <BarChart data={formats} layout="vertical" margin={{ top: 2, left: 10, right: 26, bottom: 2 }} barCategoryGap="18%">
            <CartesianGrid horizontal={false} /><XAxis type="number" tickLine={false} axisLine={false} /><YAxis dataKey="format" type="category" width={110} tickLine={false} axisLine={false} />
            <ChartTooltip content={<ChartTooltipContent />} /><Bar dataKey="listings" barSize={20} radius={[0, 10, 10, 0]}>{formats.map((row, index) => <Cell key={row.format} fill={productScale[index]} />)}<LabelList dataKey="listings" position="right" className="fill-[#4f566d] text-[11px] font-bold" /></Bar>
          </BarChart>
        </ChartContainer>
        <div className="sales-caption mt-4">
          <div className="sales-caption-meter"><span>Sales field coverage</span><div><i style={{ width: '52%' }} /></div><strong>52%</strong></div>
          <div className="sales-caption-detail"><span><b>78</b> available</span><span><b>72</b> missing</span><small>Missing stays null and is never recoded to zero.</small></div>
        </div>
      </article>
      <article className={`${cardClass} decision-panel p-5 sm:p-7`}>
        <SectionTitle eyebrow="04 · What to do next" title="Three decisions a product team could test" copy="Each recommendation starts with an observed market pattern and ends with a measurable next step." />
        <div className="decision-path mt-5">
          <article style={{ '--decision': '#FF5F8F' } as CSSProperties}><i /><div><small>Observed evidence</small><strong>137 of 150 listings are priced at CNY 100 or below</strong></div><div><small>Portfolio decision</small><strong>Define the price ladder</strong><p>Keep accessible entry products, then make design, material, and IP the visible reasons to trade up.</p></div><b>Portfolio architecture</b></article>
          <article style={{ '--decision': '#F4B63E' } as CSSProperties}><i /><div><small>Observed evidence</small><strong>71 figurines and 45 DIY kits lead the format mix</strong></div><div><small>Portfolio decision</small><strong>Merchandise by mission</strong><p>Separate collect-and-display products from discover-and-build experiences across navigation and gifting.</p></div><b>Customer journey</b></article>
          <article style={{ '--decision': '#8B5CF6' } as CSSProperties}><i /><div><small>Observed evidence</small><strong>Only 13 listings sit in premium or high-end price tiers</strong></div><div><small>Portfolio decision</small><strong>Test premium before scaling</strong><p>Run focused pilots and require conversion, margin, repeat purchase, and inventory evidence.</p></div><b>Measured experiment</b></article>
        </div>
        <div className="decision-boundary"><strong>Decision boundary</strong><span>Clusters describe positioning patterns. They do not prove authenticity, quality, or purchase causality.</span></div>
      </article>
    </div>
  );
}

function CustomerVoice() {
  return (
    <div className="space-y-4">
      <section className="grid gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <article className={`${cardClass} p-5 sm:p-7`}>
          <SectionTitle eyebrow="01 · Sentiment check" title="What does the 72.8% positive score really mean?" copy="It is the share predicted as positive by SnowNLP, not the share of all customers who are satisfied." />
          <div className="sentiment-viz mt-8">
            <div className="sentiment-track" aria-label="Sentiment distribution">
              {sentiment.map((row) => <div key={row.label} style={{ width: `${row.share}%`, background: row.color }} />)}
            </div>
            <div className="mt-5 grid gap-2 sm:grid-cols-3">
              {sentiment.map((row) => <div key={row.label} className="sentiment-legend"><span style={{ background: row.color }} /><strong>{row.share}%</strong><small>{row.label}</small></div>)}
            </div>
          </div>
          <div className="mt-6 grid grid-cols-2 gap-3"><div className="audit-score audit-pink"><span>Human-audit accuracy</span><strong>0.739</strong></div><div className="audit-score audit-purple"><span>Macro F1</span><strong>0.459</strong></div></div>
          <div className="metric-explainer"><div><strong>Accuracy</strong><p>73.9% of audited reviews received the correct pooled label overall.</p></div><div><strong>Macro F1</strong><p>Each sentiment class receives equal weight. The lower score reveals weak performance on less common classes.</p></div></div>
        </article>
        <article className={`${cardClass} p-5 sm:p-7`}>
          <SectionTitle eyebrow="02 · Signal check" title="Which review signals can the model recognize?" copy="Explicit packaging and logistics language is easier to detect. Blind-box outcomes, gifting, and value judgments need more context." />
          <div className="mt-6 space-y-3">
            {aspects.map((row) => <div key={row.aspect} className="grid grid-cols-[130px_minmax(0,1fr)_50px] items-center gap-3 text-xs sm:grid-cols-[160px_minmax(0,1fr)_58px]"><span className="font-medium">{row.aspect}</span><div className="h-3 overflow-hidden rounded-full bg-[#f3ece6]"><div className="h-full rounded-full" style={{ width: `${row.f1 * 100}%`, background: row.f1 >= 0.7 ? '#22C983' : row.f1 >= 0.45 ? '#FFC43D' : '#FF4D78' }} /></div><strong>F1 {row.f1.toFixed(2)}</strong></div>)}
          </div>
          <div className="context-note"><Info aria-hidden="true" /><div><strong>Why blind-box language needs context</strong><p>Not receiving a preferred design reflects draw uncertainty and expectation mismatch. It does not automatically mean dissatisfaction with product quality. Negation, mixed emotion, and slang also need manual review.</p></div></div>
        </article>
      </section>
      <SectionTitle eyebrow="03 · What customers discuss" title="Two broad conversations appear in the reviews" copy="LDA finds words that repeatedly occur together. The themes summarize discussion patterns; they are not sentiment scores or customer personas." />
      <section className="grid gap-4 md:grid-cols-2">
        <article className={`${cardClass} topic-card topic-pink p-6`}><div className="topic-number">1</div><div><span className="topic-label">LDA theme 1</span><h3>Collecting delight & blind-box outcome</h3><p>Discovery, craftsmanship, and the emotional reward of receiving a wanted design.</p><div className="topic-terms"><span>cute</span><span>hidden</span><span>craftsmanship</span><span>happy</span></div></div></article>
        <article className={`${cardClass} topic-card topic-blue p-6`}><div className="topic-number">2</div><div><span className="topic-label">LDA theme 2</span><h3>Gifting, children & product experience</h3><p>Reviews connect educational play and gifting with service, quality, and excavation.</p><div className="topic-terms"><span>child</span><span>gift</span><span>quality</span><span>excavation</span></div></div></article>
      </section>
    </div>
  );
}

function QualityCards({ number }: { number: string }) {
  return (
    <div className="space-y-3"><SectionTitle eyebrow={`${number} · Evidence check`} title="What can this project claim with confidence?" copy="These cards separate reproducible results, evaluated models, and conclusions the available data cannot support." /><section className="grid gap-4 md:grid-cols-3">
        {[
          { icon: CheckCircle2, title: 'Passed', kicker: 'REPRODUCIBILITY', copy: '14 automated tests · fixed random seed · source checksums', tone: 'quality-blue' },
          { icon: BrainCircuit, title: 'Evaluated', kicker: 'MODEL QUALITY', copy: 'Cluster stability · held-out LDA · sentiment and aspect F1', tone: 'quality-purple' },
          { icon: AlertTriangle, title: 'Not supported', kicker: 'BOUNDARIES', copy: 'Causality · authenticity · revenue or demand forecasting', tone: 'quality-yellow' },
        ].map((item) => <article key={item.title} className={`${cardClass} quality-card ${item.tone} p-5`}><div className="quality-icon"><item.icon className="size-5 shrink-0" /></div><div><span>{item.kicker}</span><h3>{item.title}</h3><p>{item.copy}</p></div></article>)}
    </section></div>
  );
}

function ProductModelQuality() {
  return (
    <article className={`${cardClass} model-card p-5 sm:p-6`}>
      <div className="model-heading-row"><SectionTitle eyebrow="05 · Why five groups?" title="Why use K=5 instead of four or six?" copy="Among K=2 to K=6, five groups give the best balance of separation, repeatability, and usable group size. The separation is still modest, so these remain exploratory profiles." /><div className="chart-selection">Selected model · K=5</div></div>
      <ChartContainer config={{ silhouette: { label: 'Silhouette score', color: palette[2] }, stability: { label: 'Bootstrap ARI', color: palette[0] } }} className="mx-auto mt-2 h-[245px] w-full max-w-5xl aspect-auto">
        <LineChart data={kEvaluation} margin={{ top: 8, right: 18, left: -8, bottom: 28 }}><CartesianGrid vertical={false} /><XAxis dataKey="k" tickLine={false} tickMargin={10} axisLine={{ stroke: '#625d75', strokeWidth: 1.4 }}><Label value="Candidate clusters (K)" position="insideBottom" offset={-16} /></XAxis><YAxis domain={[0.2, 1]} tickLine={false} axisLine={false} /><ReferenceLine x={5} stroke="#171A2B" strokeDasharray="4 4" /><ChartTooltip content={<ChartTooltipContent />} /><Legend verticalAlign="top" height={34} /><Line type="monotone" name="Silhouette score" dataKey="silhouette" stroke={palette[2]} strokeWidth={3} dot={{ r: 4 }} /><Line type="monotone" name="Bootstrap ARI" dataKey="stability" stroke={palette[0]} strokeWidth={3} dot={{ r: 4 }} /></LineChart>
      </ChartContainer>
    </article>
  );
}

function CustomerModelQuality() {
  return (
    <div className="space-y-4">
      <article className={`${cardClass} model-card p-5 sm:p-6`}>
        <div className="model-heading-row"><SectionTitle eyebrow="04 · Why two themes?" title="Why stop at two broad topics?" copy="When the model is forced to create more topics, it becomes worse at explaining unseen reviews. Two broad themes are therefore safer than several unstable, narrow labels." /><div className="chart-selection">Selected model · 2 topics</div></div>
        <ChartContainer config={{ perplexity: { label: 'Held-out perplexity', color: palette[3] } }} className="mx-auto mt-2 h-[245px] w-full max-w-5xl aspect-auto">
          <LineChart data={ldaEvaluation} margin={{ top: 8, right: 18, left: 0, bottom: 30 }}><CartesianGrid vertical={false} /><XAxis dataKey="topics" ticks={[2,3,4,5,6]} tickLine={false} tickMargin={10} axisLine={{ stroke: '#625d75', strokeWidth: 1.5 }}><Label value="Number of topics tested" position="insideBottom" offset={-17} fill="#4f4b60" /></XAxis><YAxis tickLine={false} axisLine={false} /><ReferenceLine x={2} stroke="#171A2B" strokeDasharray="4 4" /><ChartTooltip content={<ChartTooltipContent />} /><Line type="monotone" name="Held-out perplexity" dataKey="perplexity" stroke={palette[3]} strokeWidth={3} dot={{ r: 5, fill: '#fff', strokeWidth: 3 }} /></LineChart>
        </ChartContainer>
      </article>
      <QualityCards number="05" />
    </div>
  );
}

function StudyIntro({
  number, title, question, data, delivers, tone,
}: {
  number: string; title: string; question: string; data: string; delivers: string; tone: 'blue' | 'pink';
}) {
  return (
    <section className={`study-intro ${tone === 'blue' ? 'study-blue' : 'study-pink'}`}>
      <div className="study-heading"><span>{number}</span><div><p>{tone === 'blue' ? 'MARKET DASHBOARD' : 'CUSTOMER DASHBOARD'}</p><h2>{title}</h2></div></div>
      <div className="study-facts">
        <div><span>Business question</span><strong>{question}</strong></div>
        <div><span>Data used</span><strong>{data}</strong></div>
        <div><span>You will learn</span><strong>{delivers}</strong></div>
      </div>
    </section>
  );
}

function DashboardSwitcher({ view, onChange }: { view: View; onChange: (view: View) => void }) {
  const options = [
    { name: 'Product Landscape' as View, icon: PackageSearch, kicker: 'A · WHAT IS SOLD', copy: 'Prices, formats, product groups' },
    { name: 'Customer Voice Lab' as View, icon: MessageCircleMore, kicker: 'B · WHAT IS SAID', copy: 'Review themes and model reliability' },
  ];
  return <div className="dashboard-switcher" aria-label="Switch dashboards">{options.map((option) => <button key={option.name} type="button" aria-label={`Open ${option.name} dashboard`} onClick={() => onChange(option.name)} className={view === option.name ? 'is-active' : ''} aria-pressed={view === option.name}><option.icon aria-hidden="true" /><span><small>{option.kicker}</small><strong>{option.name}</strong><em>{option.copy}</em></span><b aria-hidden="true">↗</b></button>)}</div>;
}

export default function Home() {
  const [view, setView] = useState<View>('Product Landscape');
  const changeView = (nextView: View) => {
    setView(nextView);
    window.requestAnimationFrame(() => document.getElementById('dashboard-start')?.scrollIntoView({ behavior: 'smooth', block: 'start' }));
  };
  return (
    <main className={`site-shell ${view === 'Product Landscape' ? 'dashboard-a' : 'dashboard-b'} min-h-screen px-3 py-3 sm:px-6 sm:py-5 lg:px-10`}>
      <div className="mx-auto max-w-[1280px]">
        <nav aria-label="Dashboard views" className="site-nav sticky top-2 z-50 mb-4 flex flex-col gap-2 rounded-[1.15rem] border border-[#171A2B]/8 bg-white/90 p-2 shadow-[0_8px_24px_rgb(23_26_43/7%)] backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2 whitespace-nowrap px-2 text-[11px] font-black tracking-[0.15em] text-[#171A2B]"><span className="brand-dot shrink-0"><Sparkles className="size-3.5 shrink-0" /></span><span>CULTURE / COLLECTIBLE</span></div>
          <DashboardSwitcher view={view} onChange={changeView} />
        </nav>
        <header className="hero-editorial relative mb-6">
          <div className="hero-visual relative min-h-[260px] overflow-hidden rounded-[1.65rem] sm:min-h-[360px] sm:rounded-[2rem]">
            <Image src="/hero-museum-story-v2.png" alt="Three collectible characters exploring artifacts inside a colorful miniature museum" fill sizes="100vw" className="object-cover object-center" priority />
            <div className="hero-image-wash" />
          </div>
          <div className="hero-copy max-w-3xl text-[#252233]">
            <div className="hero-story"><div className="mb-3 flex w-fit items-center gap-2 whitespace-nowrap text-[11px] font-bold text-[#D65D85]"><Sparkles className="size-4 shrink-0" /> PRODUCT ANALYTICS · MULTILINGUAL NLP</div><h1 className="hero-title">Mapping museum collectibles<br className="hidden sm:block" /> and testing review models</h1></div>
            <div className="hero-summary"><p>150 marketplace listings reveal price and assortment structure. 500 independent reviews test topics, sentiment, and model reliability.</p><div className="hero-evidence"><span><strong>150</strong> listings</span><span><strong>500</strong> reviews</span><span><strong>180</strong> audited labels</span></div></div>
          </div>
        </header>
        <div id="dashboard-start" className="scroll-mt-24" />
        {view === 'Product Landscape' ? <div className="space-y-5"><StudyIntro number="A" title="Product Landscape" tone="blue" question="What does this market sell, at what price, and in which product forms?" data="150 public Taobao/Tmall listing snapshots; sales shown for 78" delivers="A market map, five exploratory product groups, and three decisions to test" /><Overview /><Products /><ProductModelQuality /><QualityCards number="06" /></div> : null}
        {view === 'Customer Voice Lab' ? <div className="space-y-5"><StudyIntro number="B" title="Customer Voice Lab" tone="pink" question="What do customers discuss, and when should automated analysis be trusted?" data="500 independent Chinese reviews; 180 human-audited labels" delivers="Two review themes, sentiment and aspect checks, and clear model limits" /><div className="separation-note"><AlertTriangle className="size-4 shrink-0"/><span>This review corpus is independent and cannot be joined to the 150 product listings at SKU level.</span></div><section aria-label="Customer voice metrics" className="grid gap-3 sm:grid-cols-3"><article className={`${cardClass} customer-metric metric-blue p-4`}><p>Reviews analyzed</p><strong>500</strong><span>fixed sample from 8,107 unique texts</span></article><article className={`${cardClass} customer-metric metric-yellow p-4`}><p>Labels checked by a person</p><strong>180</strong><span>used to test automated sentiment</span></article><article className={`${cardClass} customer-metric metric-pink p-4`}><p>Balanced model score</p><strong>0.459</strong><span>weak on less common sentiment classes</span></article></section><CustomerVoice /><CustomerModelQuality /></div> : null}
        <footer className="mt-6 flex flex-col gap-2 border-t border-border py-5 text-xs leading-5 text-muted-foreground sm:flex-row sm:items-center sm:justify-between"><span>Two independent studies · 150 product listings · 500 Chinese reviews</span><span>No SKU-level join · Sales shown for 78/150 listings · 180-label human audit</span></footer>
      </div>
    </main>
  );
}
