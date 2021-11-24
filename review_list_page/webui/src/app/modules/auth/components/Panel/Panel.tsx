import React from 'react'
import { StyledPanel } from './Panel.styles'

type PanelProps = {
  headerText: string
  children: React.ReactNode
  className?: string
}

export const Panel = ({ headerText, className, children }: PanelProps) => (
  <StyledPanel>
    <div className="Panel-Header">
      <h4 className="t-display">{headerText}</h4>
    </div>
    <div className={`Panel-Body ${className ? className : ''}`}>{children}</div>
  </StyledPanel>
)
