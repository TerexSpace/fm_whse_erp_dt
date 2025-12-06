% Placeholder for JUCS class file
% Please download the official jucs2e.cls from https://lib.jucs.org/jucs2e.cls
% and replace this file.

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{jucs2e}[2024/01/01 v1.0 JUCS Placeholder]

% Process options
\DeclareOption{times}{\def\jucs@times{1}}
\DeclareOption{10pt}{}
\DeclareOption{twocolumn}{}
\ProcessOptions\relax

\LoadClass[10pt,twocolumn]{article}

\RequirePackage{times}
\RequirePackage{geometry}
\geometry{a4paper, left=2cm, right=2cm, top=2.5cm, bottom=2.5cm}

% Store address for later use
\def\jucs@address{}
\newcommand{\address}[1]{\gdef\jucs@address{#1}}

% Keywords command (used after document begins)
\newcommand{\keywords}[1]{\par\addvspace\baselineskip\noindent\textbf{Keywords: }#1}

% Classification environment (used after document begins)
\newenvironment{classification}{\par\addvspace\baselineskip\noindent\textbf{Categories: }}{}

% Redefine maketitle to include address
\let\jucs@oldmaketitle\maketitle
\renewcommand{\maketitle}{%
  \jucs@oldmaketitle%
  \ifx\jucs@address\empty\else%
    \vspace{0.5\baselineskip}%
    \noindent\textit{\jucs@address}%
    \par\vspace{\baselineskip}%
  \fi%
}

\endinput
